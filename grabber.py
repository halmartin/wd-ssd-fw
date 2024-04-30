#!/usr/bin/env python3

import io
import os
import requests
import xmltodict

from urllib.parse import urlparse

class WdDownloader():
    def __init__(self):
        self.session = requests.session()

    def list_models(self, xdoc):
        return([a.get("@model") for a in xdoc.get("lista_devices", {}).get("lista_device")])

    def generate_filelist(self, xdoc, model=None):
        for a in xdoc.get("lista_devices").get("lista_device"):
            if model != None:
                if a.get("@model") == model:
                    if isinstance(a.get('url'), str):
                            yield f"https://wddashboarddownloads.wdc.com/{a.get('url')}"
                    elif isinstance(a.get('url'), list):
                        for url in a.get('url'):
                            yield f"https://wddashboarddownloads.wdc.com/{url}"
            else:
                if isinstance(a.get('url'), str):
                        yield f"https://wddashboarddownloads.wdc.com/{a.get('url')}"
                elif isinstance(a.get('url'), list):
                    for url in a.get('url'):
                        yield f"https://wddashboarddownloads.wdc.com/{url}"

    def download_firmware(self, urls, output):
        for target in urls:
            resp = self.session.get(target)
            if resp.status_code != 200:
                print(f"{target} HTTP {resp.status_code}")
                continue
            # for some reason the response contains a newline at the start of the document
            # which xml.parsers does not like
            in_doc = io.BytesIO(resp.text.strip().encode("UTF-8"))
            xdoc = xmltodict.parse(in_doc)
            path = urlparse(target).path
            fw_ver = path.split("/")[-2:][0]
            # save the name of the firmware file
            fw_file = xdoc.get("ffu", {}).get("fwfile")
            model = xdoc.get("ffu", {}).get("model")
            # this won't append a new model to the same firmware version, meh
            model_out = os.path.join(output, fw_ver, "model.txt")
            if not self.firmware_exists(model_out):
                self.write_firmware(model_out, model.encode("UTF-8"))
            fw_out = os.path.join(output, fw_ver, fw_file)
            if not self.firmware_exists(fw_out):
                fw_url = ("https://wddashboarddownloads.wdc.com/wdDashboard/firmware/" + "/".join(path.split("/")[3:-1]) + "/" + fw_file)
                fw_resp = self.session.get(fw_url)
                if fw_resp.status_code != 200:
                    print(f"{fw_url} HTTP {fw_resp.status_code}")
                else:
                    print(f"Downloaded {fw_file}")
                    # write out the firmware
                    self.write_firmware(fw_out, fw_resp.content)
    
    def firmware_exists(self, fw_file):
        if os.path.exists(fw_file):
            return True
        return False

    def write_firmware(self, out_file, fw_data):
        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))
        if not os.path.exists(out_file):
            with open(out_file, "wb") as outfile:
                outfile.write(fw_data)
            print(f"Saved {out_file}")
        else:
            print(f"{out_file} already exists!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-m", "--model", type=str, default=None, help="Download firmware for specified model")
    # parser.add_argument("-f", "--file", type=str, help="XML file to parse")
    parser.add_argument("-u", "--url", type=str, default="https://wddashboarddownloads.wdc.com/wdDashboard/config/devices/lista_devices.xml", help="Western Digital XML manifest URL")
    parser.add_argument("-o", "--output", type=str, default=os.path.dirname(os.path.realpath(__file__)), help="Directory to download firmware file(s) to")
    args = parser.parse_args()

    wd_resp = requests.get(args.url)
    # can't do much if we don't get the XML from WD
    wd_resp.raise_for_status()
    in_xml = xmltodict.parse(wd_resp.text)

    wdd = WdDownloader()
    if args.list:
        print(wdd.list_models(in_xml))
    else:
        xml_urls = [a for a in wdd.generate_filelist(in_xml, args.model)]
        wdd.download_firmware(xml_urls, args.output)
