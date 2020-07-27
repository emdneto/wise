from bs4 import BeautifulSoup

import requests
import time
import json
import requests

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
            print("Requesting data from http://10.7.227.130:9100/metrics...")
            self.metrics_request(pvt_interface_data)
            print ("Done. Restarting in 10 seconds...")
            time.sleep(10)
        #This print should not be reached by the code unless the loop can't find any information about the pvt interface data
        print ("Problem while searching for pvvt interface data, no data found. Closing service...")

    def metrics_request(self, pvt_interface_data):
        metrics = requests.get("http://10.7.227.130:9100/metrics").content
        print("Metric successfuly requested, printing entire request:")
        metricsRaw = BeautifulSoup(metrics, 'html.parser')
        print(metricsRaw)
        print ("Calling metrics parser...")
        self.metricsParser(metricsRaw, pvt_interface_data)

    def metricsParser(self, metricsRaw, pvt_interface_data):
        print ("Iterating over all metrics to find pvt interface data...")
        for line in metricsRaw.prettify().split("\n"):
            #print (line)
            if 'wifi_network_quality{mode' in line:
                print (line)
                if 'ssid="pvt-ssid"' in line:
                  #Extract private interface name from the entire line...
                  pvt_interface_data = line
                  pvt_interface_data_name = pvt_interface_data.split("{")[1].split(",")[1].split("=")[1][1:][:-1]
                  print ("Private interface name find: " + pvt_interface_data_name)
                  print ("Searching for number of active stations...")
                  for line2 in metricsRaw.prettify().split("\n"):
                      if 'wifi_stations{ifname="' + pvt_interface_data_name in line2:
                          pvt_interface_stations_num = line2.split(" ")

                  print ("Number of active wifi_stations: " + pvt_interface_stations_num[1])

                  if "0" in pvt_interface_stations_num:
                      print ("0 stations active, adding a occurrence and checking for 10 consecutive 0 occurrences.")
                      self.addZeroOccurrence()
                      self.checkZeroOccurrences(pvt_interface_data_name)
                  else:
                      self.resetList()

        if pvt_interface_data is None:
            print ("no pvt interface data was find on metric response!")
            active_loop = 0

    def checkZeroOccurrences(self, pvt_interface_data_name):
        if (len(zero_occurrences) == 10):
            print("10 occurrences reached, activating elasticy method!")
            self.callElasticyMechanism(pvt_interface_data_name)

    def addZeroOccurrence(self):
        print ("Zero wifi_stations detected, registring the occurrence...")
        zero_occurrences.append("0")

    def resetList(self):
        zero_occurrences.clear()

    def callElasticyMechanism(self, pvt_interface_data_name):
        print ("Elasticy method called...")

        self.metrics_request_pub(pvt_interface_data_name)
        #Do Something...

    def metrics_request_pub(self, pvt_interface_data_name):
        print("Requesting metrics to search for the pub interface data")
        metrics = requests.get("http://10.7.227.130:9100/metrics").content
        print("Metrics successfuly gathered, printing entire Requisition:")
        metricsRaw = BeautifulSoup(metrics, 'html.parser')
        print(metricsRaw)
        print ("Calling metrics parser...")
        self.metricsParser_pub(metricsRaw, pvt_interface_data_name)

    def metricsParser_pub(self, metricsRaw, pvt_interface_data_name):
        print ("Metrics parser called, searching for pub interface data...")
        for line in metricsRaw.prettify().split("\n"):
            #print (line)
            if 'wifi_network_quality{mode' in line:
                print (line)
                if 'ssid="pub-ssid"' in line:
                  #Extract public interface name from the entire line...
                  pub_interface_data = line
                  pub_interface_data_name = pub_interface_data.split("{")[1].split(",")[1].split("=")[1][1:][:-1]
                  print("Pub interface data found! calling requesition mechanism!")
                  self.requestChanges(pub_interface_data_name, pvt_interface_data_name)

    def requestChanges(self, pub_interface_data_name, pvt_interface_data_name):
        print("Building Json body of HTTP requisiton")
        Jsonrequest = {"slice_id":1,"pcpe_ip_address":"172.17.0.2","ssids":[{"ssid_name": "pCPE1Pub","ctrl_port_name":pub_interface_data_name,"bw_burst":5,"bw_rate":6},
		{"ssid_name":"pCPE1Priv","ctrl_port_name":pvt_interface_data_name,"bw_burst":5,"bw_burst":6}]}
        jsonData = json.dumps(Jsonrequest)
        print("JSON body builded, printing:")
        print(jsonData)
        print("Making HTTP Post requisition to http://10.7.229.85:8089/necos/wscagent/ssid/update")
        response = requests.post('http://10.7.229.85:8089/necos/wscagent/ssid/update', Jsonrequest)
        print("Requisition made...")
        print("Request reponse status code: ", response.status_code)
        print("Printing Entire Post Request")
        print(response.json())

if __name__ == "__main__":
    start = pcpe_metrics_collector()
    start.start()
