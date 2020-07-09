from bs4 import BeautifulSoup

import requests
import time

class pcpe_metrics_collector:

    global pvt_interface_data
    global pvt_interface_stations_num
    global zero_occurrences

    global active_loop

    def start(self):
        pvt_interface_data = None
        zero_occurrences = list()
        active_loop = 1
        while(active_loop):
            self.metrics_request(pvt_interface_data)
            print ("Done. Restarting in 10 seconds...")
            time.sleep(10)
        #This print should not be reached by the code unless the loop can't find any information about the pvt interface data
        print ("Problem while searching for pvvt interface data, no data found. Closing service...")

    def metrics_request(self, pvt_interface_data):
        metrics = requests.get("http://10.7.227.130:9100/metrics").content
        metricsRaw = BeautifulSoup(metrics, 'html.parser')
        #print ("Calling metric parser...")
        self.metricsParser(metricsRaw, pvt_interface_data)

    def metricsParser(self, metricsRaw, pvt_interface_data):
        #print ("Metrics parser called")
        for line in metricsRaw.prettify().split("\n"):
            #print (line)
            if 'wifi_network_quality{mode' in line:
                print (line)
                if 'ssid="pvt-ssid"' in line:
                  #Extract private interface name from the entire line...
                  pvt_interface_data = line
                  pvt_interface_data_name = pvt_interface_data.split("{")[1].split(",")[1].split("=")[1][1:][:-1]
                  print ("Private interface name: " + pvt_interface_data_name)
                  for line2 in metricsRaw.prettify().split("\n"):
                      if 'wifi_stations{ifname="' + pvt_interface_data_name in line2:
                          pvt_interface_stations_num = line2.split(" ")

                  print ("Number of active wifi_stations: " + pvt_interface_stations_num[1])

                  if "0" in pvt_interface_stations_num:
                      self.addZeroOccurrence()
                      self.checkZeroOccurrences()
                  else:
                      self.resetList()

        if pvt_interface_data is None:
            active_loop = 0

    def checkZeroOccurrences(self):
        if (len(zero_occurrences) == 10):
            self.callElasticyMechanism()

    def addZeroOccurrence(self):
        print ("Zero wifi_stations detected, registring the occurrence...")
        zero_occurrences.append("0")

    def resetList(self):
        zero_occurrences.clear()

    def callElasticyMechanism(self):
        print ("Elasticy method called...")
        #Do Something...

if __name__ == "__main__":
    start = pcpe_metrics_collector()
    start.start()
