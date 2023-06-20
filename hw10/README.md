Single thread handler execution time:
> time python memc_load_.py --pattern="*.tsv.gz"

real  6m30.120s

4-workers multi-threaded handler execution time:
> time python memc_conc_load.py --pattern="*.tsv.gz"

real  2m45.365s
