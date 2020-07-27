import os
import logging
import requests
import asyncio
from bs4 import BeautifulSoup
import logging
import sys
import time
import json


root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


class Focus:

    def __init__(self):
        #self.pvt_interface_data = ''
        self.pvt_interface_data_name = ''
        self.pub_interface_data_name = ''
        self.pvt_name = 'wise-pvt'
        self.pub_name = 'wise-pub'
        self.pvt_interface_stations_num = 0
        self.zero_occurrences = []
        self.run = True
        self.collect = 1
        self.log = logging.getLogger('focus')
        self.collectTime = 10
        self.treshold = 10
        self.total_band = 5
        self.changed = False

    def start(self):
        self.log.info('Starting Focus.')
        self.log.info(
            'Collecting data from http://10.7.227.130:9100/metrics...')
        while self.run:

            try:
                self.log.info(f'Collect Iteration Nº {self.collect}')
                self.metrics_request()
                self.log.info(
                    f'Done. Restarting  in {self.collectTime} seconds...')
                time.sleep(self.collectTime)
                self.collect += 1
            except Exception as e:
                err = str(e)
                self.log.error(f'Error: {err}')

    def metrics_request(self):

        try:
            metrics = requests.get("http://10.7.227.130:9100/metrics").content
        except Exception as e:
            err = str(e)
            self.log.error(f'Error: {err}')

        metricsRaw = BeautifulSoup(metrics, 'html.parser')
        self.log.info(f'Successfuly collected. Parsing data')
        self.metricsParser(metricsRaw)

    def metricsParser(self, metricsRaw):
        self.log.info(
            "Iterating over all metrics to find pvt interface data...")
        pvt_interface_data = ''
        pub_interface_data = ''

        for line in metricsRaw.prettify().split("\n"):
            if 'wifi_network_quality{mode' in line:

                if f'ssid="{self.pvt_name}"' in line:
                    # Extract private interface name from the entire line...
                    pvt_interface_data = line
                    self.pvt_interface_data_name = pvt_interface_data.split("{")[1].split(",")[
                        1].split("=")[1][1:][:-1]
                    self.log.info("Private interface name find: " +
                                  self.pvt_interface_data_name)
                    self.log.info("Searching for number of active stations...")
                    for line2 in metricsRaw.prettify().split("\n"):
                        if 'wifi_stations{ifname="' + self.pvt_interface_data_name in line2:
                            self.pvt_interface_stations_num = line2.split(" ")[
                                1]

                    self.log.info(
                        "Number of active pvt wifi_stations: " + self.pvt_interface_stations_num)
                    
                    if int(self.pvt_interface_stations_num) > 0 and self.changed:
                        print('revert')
                        self.changed = False
                        self.revertDefault()
                        
                    if "0" in self.pvt_interface_stations_num:
                        self.log.info(
                            "0 stations active, adding a occurrence and checking for 10 consecutive 0 occurrences.")
                        self.addZeroOccurrence()
                        self.checkZeroOccurrences()
                    else:
                        self.resetList()

                if f'ssid="{self.pub_name}"' in line:
                    # Extract public interface name from the entire line...
                    pub_interface_data = line
                    self.pub_interface_data_name = pub_interface_data.split("{")[1].split(",")[
                        1].split("=")[1][1:][:-1]
                    self.log.info(
                        f"Pub interface data found: {self.pub_interface_data_name}!")

        if pvt_interface_data is '' or pub_interface_data is '':
            #self.run = False
            self.log.error(
                "No pvt or pub interface data was find on metric response! Trying again")
            # os._exit(1)

    def checkZeroOccurrences(self):
        if (len(self.zero_occurrences) == self.treshold):
            self.log.info(f"{self.treshold} occurrences reached, activating elasticy method!")
            self.callElasticyMechanism()
            self.changed = True

    def addZeroOccurrence(self):
        self.log.info(
            "Zero wifi_stations detected, registring the occurrence...")
        self.zero_occurrences.append("0")
        # self.metricsParser(metricsRaw)

    def resetList(self):
        self.zero_occurrences.clear()

    def callElasticyMechanism(self):
        self.log.info("Requesting WSCAgent Elasticity...")
        self.requestChanges()

    def requestChanges(self):
        self.log.info("Building Json body of HTTP request")

        pubRate = self.total_band * 0.8
        pvtRate = self.total_band * 0.2

        pubBurst = 8 * 1048576
        pvtBurst = 2 * 1048576

        Jsonrequest = {
            "slice_id": 1,
            "pcpe_ip_address": "10.7.227.130",
            "ssids": [{
                "ssid_name": self.pub_name,
                "ssid_bridge_name": self.pub_interface_data_name,
                "bw_burst": pubBurst,
                "bw_rate": pubRate},
                {"ssid_name": self.pvt_name,
                 "ssid_bridge_name": self.pvt_interface_data_name,
                 "bw_rate": pvtRate,
                 "bw_burst": pvtBurst}]}

        jsonData = json.dumps(Jsonrequest)
        self.log.debug(jsonData)
        self.log.info(
            "Making HTTP Post request to http://10.7.229.85:8089/necos/wscagent/ssid/update")
        response = requests.post(
            'http://10.7.229.85:8089/necos/wscagent/ssid/update', Jsonrequest)
        self.log.info("Request reponse status code: ", response.status_code)
        self.log.info(response.json())

    def revertDefault(self):
        self.log.info("Building Json body of HTTP request")

        pubRate = self.total_band * 0.2
        pvtRate = self.total_band * 0.8

        pubBurst = 2 * 1048576
        pvtBurst = 8 * 1048576

        Jsonrequest = {
            "slice_id": 1,
            "pcpe_ip_address": "10.7.227.130",
            "ssids": [{
                "ssid_name": self.pub_name,
                "ssid_bridge_name": self.pub_interface_data_name,
                "bw_burst": pubBurst,
                "bw_rate": pubRate},
                {"ssid_name": self.pvt_name,
                 "ssid_bridge_name": self.pvt_interface_data_name,
                 "bw_rate": pvtRate,
                 "bw_burst": pvtBurst}]}

        jsonData = json.dumps(Jsonrequest)
        self.log.debug(jsonData)
        self.log.info(
            "Making HTTP Post request default to http://10.7.229.85:8089/necos/wscagent/ssid/update")
        response = requests.post(
            'http://10.7.229.85:8089/necos/wscagent/ssid/update', Jsonrequest)
        self.log.info("Request reponse status code: ", response.status_code)
        self.log.info(response.json())


if __name__ == "__main__":
    try:
        f = Focus()
        f.start()
    except Exception as e:
        err = str(e)
        root.error(f'Failed, {err}')
