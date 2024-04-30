# Usage

```
./grabber.py [-l|--list] [-m|--model] [-u|--url] [-o|--output=/path/to/output]
```

* list: list all models from Western Digital's XML manifest
* model: download the firmware only for the specified model
* url: specify an alternate URL to download the XML manifest from
* output: directory to write downloaded firmware files to

# Motivation

Western Digital do not provide a firmware update tool for non-Windows operating systems.

Framework are selling Western Digital NVMe SSDs with known issues, and it was annoying to do the manual steps outlined [on the Framework community](https://community.frame.work/t/western-digital-drive-update-guide-without-windows-wd-dashboard/20616) to download the `.fluf` file, so I wrote a script to automate downloading the files.

# Limitations

Firmware URLs for SanDisk models are HTTP 404. Guess the download URL for those files is different.
