#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
import os
import gzip
import pdb
import sys
import glob
import logging
import collections
from optparse import OptionParser

# brew install protobuf
# protoc  --python_out=. ./appsinstalled.proto
# pip install protobuf
import appsinstalled_pb2

# pip install python-memcached
import memcache

NORMAL_ERR_RATE = 0.01
AppsInstalled = collections.namedtuple(
    "AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"]
)

batch_size = 100


def create_pool(opts):
    return {
        "idfa": memcache.Client([opts.idfa]),
        "gaid": memcache.Client([opts.gaid]),
        "adid": memcache.Client([opts.adid]),
        "dvid": memcache.Client([opts.dvid]),
    }


def dot_rename(path):
    head, fn = os.path.split(path)
    # atomic in most cases
    os.rename(path, os.path.join(head, "." + fn))


def insert_appsinstalled(memc_conn, buffer, dry_run=False):
    try:
        if dry_run:
            logging.debug(f"uploaded buffer {buffer}")
        else:
            memc = memc_conn
            memc.set_multi(dict(buffer), time=100)
    except Exception as e:
        logging.exception("Cannot write to memc %s: %s" % (memc_conn, e))
        return False
    return True


def serialize_appsinstalled(appsinstalled):
    ua = appsinstalled_pb2.UserApps()
    ua.lat = appsinstalled.lat
    ua.lon = appsinstalled.lon
    key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
    ua.apps.extend(appsinstalled.apps)
    packed = ua.SerializeToString()

    return key, packed


def parse_appsinstalled(line):
    line_parts = line.strip().split("\t")
    if len(line_parts) < 5:
        return
    dev_type, dev_id, lat, lon, raw_apps = line_parts
    if not dev_type or not dev_id:
        return
    try:
        apps = [int(a.strip()) for a in raw_apps.split(",")]
    except ValueError:
        apps = [int(a.strip()) for a in raw_apps.split(",") if a.isidigit()]
        logging.info("Not all user apps are digits: `%s`" % line)
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        logging.info("Invalid geo coords: `%s`" % line)
    return AppsInstalled(dev_type, dev_id, lat, lon, apps)


def start_workers(opts):
    for fn in glob.iglob(opts.pattern):
        filesize = os.stat(fn).st_size
        chunk_size = filesize // 4

        processes = []

        try:
            for i in range(4):
                start = i * chunk_size
                end = start + chunk_size if i < 3 else filesize
                process = multiprocessing.Process(target=main, args=(opts, start, end))
                process.start()
                processes.append(process)

            for process in processes:
                process.join()

        except Exception as e:
            logging.exception(f"Unexpected error")


def main(options, start, end):
    conn_pool = create_pool(options)
    buffers = {
        "idfa": [],
        "gaid": [],
        "adid": [],
        "dvid": [],
    }
    for fn in glob.iglob(options.pattern):
        processed = errors = 0
        logging.info("Processing %s" % fn)
        fd = gzip.open(fn, "r")
        fd.seek(start)
        fd_lines = fd.readlines(end - start)
        for line in fd_lines:
            print(line)
            line = line.decode()
            line = line.strip()
            if not line:
                continue
            appsinstalled = parse_appsinstalled(line)
            if not appsinstalled:
                errors += 1
                continue
            mem_conn = conn_pool.get(appsinstalled.dev_type)
            if not mem_conn:
                errors += 1
                logging.error("Unknow device type: %s" % appsinstalled.dev_type)
                continue
            ok = serialize_appsinstalled(mem_conn)
            if ok:
                processed += 1
                if appsinstalled.dev_type == "idfa":
                    buffers["idfa"].append(ok)
                elif appsinstalled.dev_type == "gaid":
                    buffers["gaid"].append(ok)
                elif appsinstalled.dev_type == "adid":
                    buffers["adid"].append(ok)
                elif appsinstalled.dev_type == "dvid":
                    buffers["dvid"].append(ok)
            else:
                errors += 1

            for buffer in buffers:
                if len(buffer) == batch_size:
                    mem_conn = conn_pool.get(buffer)
                    insert_appsinstalled(mem_conn, buffer, options.dry)

        for buffer in buffers:
            mem_conn = conn_pool.get(buffer)
            insert_appsinstalled(mem_conn, buffer, options.dry)
        if not processed:
            fd.close()
            dot_rename(fn)
            continue
        err_rate = float(errors) / processed
        if err_rate < NORMAL_ERR_RATE:
            logging.info("Acceptable error rate (%s). Successfull load" % err_rate)
        else:
            logging.error(
                "High error rate (%s > %s). Failed load" % (err_rate, NORMAL_ERR_RATE)
            )
        fd.close()
        try:
            dot_rename(fn)
        except FileNotFoundError:
            pass


def prototest():
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-t", "--test", action="store_true", default=False)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="/data/appsinstalled/*.tsv.gz")
    op.add_option("--idfa", action="store", default="127.0.0.1:33013")
    op.add_option("--gaid", action="store", default="127.0.0.1:33014")
    op.add_option("--adid", action="store", default="127.0.0.1:33015")
    op.add_option("--dvid", action="store", default="127.0.0.1:33016")
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO if not opts.dry else logging.DEBUG,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    if opts.test:
        prototest()
        sys.exit(0)

    start_workers(opts)
