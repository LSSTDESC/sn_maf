import matplotlib.pyplot as plt
import lsst.sims.maf.metricBundles as metricBundles
import lsst.sims.maf.slicers as slicers
import lsst.sims.maf.db as db
import lsst.sims.maf.utils as utils
import argparse
import time
import yaml
from importlib import import_module
import sqlite3

parser = argparse.ArgumentParser(
    description='Run a SN metric from a configuration file')
parser.add_argument('config_filename',
                    help='Configuration file in YAML format.')

def run(config_filename):
    # YAML input file.
    config = yaml.load(open(config_filename))
    #print(config)
    outDir ='Test' # this is for MAF

    # grab the db filename from yaml input file 
    dbFile=config['Observations']['filename']

    """
    conn = sqlite3.connect(dbFile)
    cur = conn.cursor()
    table_name='Proposal'
    result = cur.execute("PRAGMA table_info('%s')" % table_name).fetchall()
    print('Results',result)

    cur.execute("SELECT * FROM Proposal")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    print('end')
    cur.execute('PRAGMA TABLE_INFO({})'.format('ObsHistory'))
    
    names = [tup[1] for tup in cur.fetchall()]
    print(names)
    """
    opsimdb = db.OpsimDatabase(dbFile)
    version = opsimdb.opsimVersion
    propinfo, proptags = opsimdb.fetchPropInfo()
    print('proptags and propinfo',proptags,propinfo)

    # grab the fieldtype (DD or WFD) from yaml input file
    fieldtype = config['Observations']['fieldtype']
    
    module = import_module(config['Metric'])
    
    slicer = slicers.HealpixSlicer(nside=config['Pixelisation']['nside'])

    # print('slicer',slicer.pixArea,slicer.slicePoints['ra'])
    
    metric=module.SNMetric(config=config,coadd=config['Observations']['coadd'])
    
    sqlconstraint = opsimdb.createSQLWhere(fieldtype, proptags)
    
    mb = metricBundles.MetricBundle(metric, slicer, sqlconstraint)
    
    mbD = {0:mb}

    resultsDb = db.ResultsDb(outDir=outDir)

    mbg =  metricBundles.MetricBundleGroup(mbD, opsimdb,
                                      outDir=outDir, resultsDb=resultsDb)

    mbg.runAll()
    
    #mbg.plotAll(closefigs=False)
    #plt.show()

def main(args):
    print('running')
    time_ref = time.time()
    run(args.config_filename)
    print('Time', time.time()-time_ref)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
