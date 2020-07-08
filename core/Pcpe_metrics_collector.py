from bs4 import BeautifulSoup

import requests
import time

class Pcpe_metrics_collector:

    global pvt_interface_data
    global pvt_interface_stations_num
    global zero_occurrences

    def start(self):
        zero_occurrences = list()
        while(1):
            self.metrics_request()
            print ("Done. Restarting in 10 seconds...")
            time.sleep(10)

    def metrics_request(self):
        metrics = requests.get("http://10.7.227.130:9100/metrics").content
        metricsRaw = BeautifulSoup(metrics, 'html.parser')
        self.metricsParser(metricsRaw)

    def metricsParser(self, metricsRaw):
        for line in metricsRaw.prettify().split("\n"):
            if 'wifi_network_quality{mode' in line:
              if 'ssid="pvt-ssid"' in line:
                pvt_interface_data = line
        #Extract private interface name from the entire line...
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
    start = Pcpe_metrics_collector()
    start.start()
