import os
import re
import base64

#from django.core.cache import cache
from django.conf import settings

patternObj = re.compile(r"""<img\s+[^>]*?src=(?P<quote>["\'])?(?P<image>[^"\'>]+)(?(quote)(?P=quote))[^>]*?>""")

class ImageDataURIMiddleware(object):

	def __init__(self):
	
		try:
			if hasattr(settings,'IMAGEDATAURI_MAX_IMAGE_SIZE'):
				self.maximum_image_size = settings.IMAGEDATAURI_MAX_IMAGE_SIZE
			if hasattr(settings,'MEDIA_ROOT'):
				self.media_root = settings.MEDIA_ROOT
		except: pass
		
		if not self.maximum_image_size:
			self.maximum_image_size = 2048;	
	
	#def process_request (self,request) : pass
	#def process_view(self,request,view_func,view_args, view_kwargs) : pass
	#def process_exception(self, request, exception) : pass
	
	def process_response(self, request, response):
		
		if response.status_code != 200:
			return response

		#ie doesn't support this, except 8
		try:
			if "msie" in request.META.get('HTTP_USER_AGENT', '').lower():
				return response
		except: pass
		
		image_names = self.find_images(response.content)
		
		if image_names == 0:
			return response
		else:
			image_data = self.images_to_base64(image_names)
			content = self.replace_images(response.content,image_data)
			response.content = content
			return response
	
	def find_images(self,page):
		matchObj = patternObj.findall(page)
		imagesCount = len(matchObj)
		if imagesCount == 0:
			return 0
		return matchObj
	
	def replace_images(self,page,image_data):
		for image in image_data:
			page = page.replace(image,image_data[image])
		return page

	def images_to_base64(self,images):
		image_data = {}
		for line in images:
			filename = str(line[1])
			if filename.find("\\") > -1 or filename.find('..') > -1 or filename.find('/') > -1:
				continue;
			if filename.find('.') > -1:
				image_ext = filename.rsplit('.').pop()
			else:
				image_ext = 'unknown'
			try:
				fsize = 0
				fsize = os.path.getsize(media_root + str(filename))
			except: pass
			if self.maximum_image_size == 0 or fsize < self.maximum_image_size:
				fp = False 			
				try:
					fp = open(self.media_root + filename,'r')
				except:
					print "could not open:" + self.media_root + str(filename)					
				if fp:		
					new_src = 'data:image/' + image_ext + ';base64,' + base64.encodestring(fp.read()).rstrip("\n")			
					image_data[filename] = new_src
					fp.close()
		return image_data



