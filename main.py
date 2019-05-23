#coding=utf-8
import argparse
import easydl2labelImg
parser = argparse.ArgumentParser()
parser.add_argument('-dataset_id', type=int,help='input dataset_id of Easydl object detection')
parser.add_argument('-xmlpath', help='LabelImg working directory')
args = parser.parse_args()
if args.dataset_id is None or args.xmlpath is None:
	print("Run \"python main.py -h\" for help")
else:
	easydl2labelImg.downloaddateset(args.dataset_id,args.xmlpath)