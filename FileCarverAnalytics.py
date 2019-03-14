#! /usr/bin/python

import os, re, sys, logging, subprocess, hashlib, types, sqlite3, argparse

try:
	from sqlalchemy import Column, Integer, Float, String, Text
	from sqlalchemy.ext.declarative import declarative_base
	from sqlalchemy.orm import sessionmaker
	from sqlalchemy import create_engine

	import simplekml

	from PIL import Image
	from PIL.ExifTags import TAGS

	from pygeocoder import Geocoder
	
	import pyPdf
	from pyPdf import PdfFileReader

	import mechanize

	import bs4

except ImportError as e:
	print "Module `{0}` not installed".format(error.message[16:])
	sys.exit()

# === SQLAlchemy Config ============================================================================
Base = declarative_base()

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

# === Database Classes =============================================================================

class sqliteDatabaseInfo(Base):

	__tablename__ = 'ImageFiles'

	id = Column(Integer,primary_key = True)
	Filename = Column(String)
	MD5 = Column(String)
	Metadata = Column(String)


	def __init__(self,Filename,MD5,Metadata):
		self.Filename = Filename
		self.MD5 = MD5
		self.Metadata = Metadata

# === File Carving Class =========================================================================
class fileCarver(object):
	def __init__(self, img = ''):
		if img == '' or not os.path.exists(img):
			raise Exception('No disk image provided')
		self.img = img
		self.fn  = os.path.splitext(os.path.basename(img))[0]
		self.dir = '{0}/extract/{1}'.format(os.path.dirname(os.path.abspath(__file__)), self.fn)
		if not os.path.exists(self.dir): os.makedirs(self.dir)

		self.db = 'filesCarved.db'
		self.engine = create_engine('sqlite:///'+self.db, echo=False)
		Base.metadata.create_all(self.engine)

		Session = sessionmaker(bind=self.engine)
		self.session = Session()
		
	def carve(self):
		try:
			subprocess.check_output(["tsk_recover","-e",self.img,self.dir])
		except:
			raise Exception('Error carving image.')

	def retrieveExif(self, img):
		exif = {}
		try:
			info = img._getexif()
			for tag, value in info.items():
				decoded = TAGS.get(tag, tag)
				# if decoded in IMG_TAGS:
				exif[decoded] = value
			try:
				exif['Latitude'] = self._retrieveImgGps(exif['GPSInfo'][2], exif['GPSInfo'][1])
				exif['Longitude'] = self._retrieveImgGps(exif['GPSInfo'][4], exif['GPSInfo'][3])
			except:
				exif['Latitude'] = exif['Longitude'] = 0.0
		except Exception as e:
			exif = exif
		return exif

	def retrieveImgGps(self, data, ref):
		coords = [float(x)/float(y) for x, y in data]
		res =  coords[0] + coords[1]/60 + coords[2]/3600
		return res if ref not in ('S', 'W') else res * -1

	def getPDFMeta(self, fn):
		pdfExif = {}
		try:
			pdf = pyPdf.PdfFileReader(open(fn, 'rb'))
			info = pdf.getDocumentInfo()
			for item, dat in info.items():
				try:
					pdfExif[item] = pdf.resolvedObjects[0][1][item]
				except:
					pdfExif[item] = dat
		except Exception as e:
			pass
		return pdfExif

	def md5Hasher(self, fullPath):
		try:
			file = open(fullPath,'rb').read()
		except:
			return
		md5Hash = hashlib.md5(file).hexdigest()
		return md5Hash

	def addDBRow(self, fileName, md5Hash, metadata):
		row = sqliteDatabaseInfo(fileName, md5Hash, metadata)
		self.session.add(row)
		self.session.commit()
		

	def report(self, dbFile):
		DATABASE = sqlite3.connect(dbFile)
		cur = DATABASE.cursor()
		with open("Final Report.txt", 'w') as file:
			data = cur.execute("SELECT * FROM ImageFiles")
			count = 1
			for row in data:
				file.write("File #{}\n".format(count))
				file.write("Filename: {}\n\n".format(row[1]))
				file.write("MD5Hash: {}\n\n".format(row[2]))
				file.write("Metadata: {}\n\n".format(row[3]))
				file.write("---------------------------------------------------------------\n\n")
				count += 1
		file.close()

def main():

# ---- For Parsing Purposes If Needed--------------------------------
	#parser = argparse.ArgumentParser(description='File Extractor from Image')
	#parser.add_argument('-f', '--file', help='Specify an image file')
	#args = parser.parse_known_args()
	
	#if len(args) < 1:
	#	print 'Image file not specified'
	#	exit(0)
	#imgs = args[1]
# ---- For Parsing Purposes If Needed--------------------------------


	imgs = ['.\\File1.163b3a010e0a50e264deb098c77daea7.001', '.\\File2.16c023257b0642f046e9a72ce7a2239a.001']
	for img in imgs:
		osf = fileCarver(img)
		osf.carve()
	
	for dirname, dirnames, filenames in os.walk("{}\{}".format(".", "extract")):
		for fn in filenames:
			fullFilePath = os.path.join(dirname, fn).lower()
			dirfile, ext = os.path.splitext(fn)
			fn = fn.decode('ascii', 'ignore')
			try:
				img = Image.open(fullFilePath)
				metadata = osf.retrieveExif(img)
				img.close()
				osf.addDBRow(fn, osf.md5Hasher(fullFilePath), str(metadata))
				continue
			except Exception, e:
				if ext == ".pdf":				
					pdf = fullFilePath
					metadata = osf.getPDFMeta(fullFilePath)
					osf.addDBRow(fn, osf.md5Hasher(fullFilePath), str(metadata))
					continue
				else:
					metadata = {}
					osf.addDBRow(fn, osf.md5Hasher(fullFilePath), str(metadata))
					
	osf.report("filesCarved.db")
	print 'All images analyzed. Extracted files saved in `./extract/`. Image information saved in `filesCarved.db`'

if __name__ == '__main__': main()