import xml.etree.ElementTree as et
import os
import obspy as obs
from obspy.fdsn import Client
from obspy.core.util.geodetics import gps2DistAzimuth
from glob import glob
import antconfig as cfg

#==============================================================================================

def read_xml(filename):
    
    def recursive_dict(element):
        return element.tag, \
            dict(map(recursive_dict, element)) or element.text
    
    
    doc = et.parse(filename)
    
    return recursive_dict(doc.getroot())

#==============================================================================================

def find_coord(path_to_xml):
    tree=et.parse(path_to_xml)
    root=tree.getroot()
    
    sta=path_to_xml.split('/')[-1].split('.')[1]

    lat=root.find('*//Station').find('Latitude').text
    lon=root.find('*//Station').find('Longitude').text
    return sta, float(lat),float(lon)
    
#==============================================================================================
    
def get_staxml(net,sta):
    client=Client()
    outfile=cfg.datadir+'/stationxml/'+net+'.'+sta+'.xml'

    # Metadata request with obspy
    if os.path.exists(outfile)==False:
        client.get_stations(network=net,station=sta,filename=outfile)
        os.system('UTIL/ch_rootelem.sh '+outfile)

#==============================================================================================

def get_coord_dist(net1, sta1, net2, sta2):

    try:
        stafile1=glob(cfg.datadir+'/stationxml/'+net1+'.'+sta1+'*.xml')[0]
    
    except IndexError:
        print 'Have to go get stationxml nr. 1'
        get_staxml(net1,sta1)
        
    
    try:
        stafile2=glob(cfg.datadir+'/stationxml/'+net2+'.'+sta2+'*.xml')[0]    
        
    except IndexError:
        print 'Have to go get stationxml nr. 2'
        get_staxml(net2,sta2)
            
    (staname1,lat1,lon1)=find_coord(cfg.datadir+'/stationxml/'+net1+'.'+sta1+'.xml')
    (staname2,lat2,lon2)=find_coord(cfg.datadir+'/stationxml/'+net2+'.'+sta2+'.xml')
    dist=gps2DistAzimuth(lat1, lon1, lat2, lon2)[0]
    az=gps2DistAzimuth(lat1, lon1, lat2, lon2)[1]
    baz=gps2DistAzimuth(lat1, lon1, lat2, lon2)[2]
    
    #except:
    #    (lat1, lon1, lat2, lon2, dist)=('?', '?','?','?','?')
    
    return (lat1, lon1, lat2, lon2, dist, az, baz)

#==============================================================================================
    
def get_sta_info(indir,network,verbose):
    
    if network=='*':
        os.system('ls '+indir+' > temp.txt')
    else:
        os.system('ls '+indir+' | grep ^'+network+'\. > temp.txt')
    
    fileid=open('temp.txt')
    filelist=fileid.read().split('\n')
    fileid.close()
    
    for file in filelist:
        if verbose: print file
        if file=='': continue
        
        if network=='*':
            network=file.split('.')[0]
        sta=file.split('.')[1]
        if sta=='*':
            str=obs.read(indir+'/'+file)
            for tr in str:
                get_staxml(tr.stats.network,tr.stats.station)
        else:
            get_staxml(network,sta)
    
    os.system('rm temp.txt')



