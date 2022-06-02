import time
import numpy as np
import os
#import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
import easyocr

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
from object_detection.utils import ops as utils_ops

if StrictVersion(tf.__version__) < StrictVersion('1.9.0'):
  raise ImportError('Please upgrade your TensorFlow installation to v1.9.* or later!')

from utils import label_map_util

from utils import visualization_utils as vis_util


# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_FROZEN_GRAPH = 'model.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('object-detection.pbtxt')


detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.compat.v1.GraphDef()
  with tf.compat.v2.io.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)


def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

# For the sake of simplicity we will use only 2 images:
# image1.jpg
# image2.jpg
# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
PATH_TO_TEST_IMAGES_DIR = 'test_images'

#Image Path 
image_path = 'test.jpg'

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)

def run_inference_for_single_image(image, graph):
  with graph.as_default():
    with tf.compat.v1.Session() as sess:
      # Get handles to input and output tensors
      ops = tf.compat.v1.get_default_graph().get_operations()
      all_tensor_names = {output.name for op in ops for output in op.outputs}
      tensor_dict = {}
      for key in [
          'num_detections', 'detection_boxes', 'detection_scores',
          'detection_classes', 'detection_masks'
      ]:
        tensor_name = key + ':0'
        if tensor_name in all_tensor_names:
          tensor_dict[key] = tf.compat.v1.get_default_graph().get_tensor_by_name(
              tensor_name)
      if 'detection_masks' in tensor_dict:
        # The following processing is only for single image
        detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
        detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
        # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
        real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
        detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
        detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            detection_masks, detection_boxes, image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(
            tf.greater(detection_masks_reframed, 0.5), tf.uint8)
        # Follow the convention by adding back the batch dimension
        tensor_dict['detection_masks'] = tf.expand_dims(
            detection_masks_reframed, 0)
      image_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name('image_tensor:0')

      # Run inference
      output_dict = sess.run(tensor_dict,
                             feed_dict={image_tensor: np.expand_dims(image, 0)})

      # all outputs are float32 numpy arrays, so convert types as appropriate
      output_dict['num_detections'] = int(output_dict['num_detections'][0])
      output_dict['detection_classes'] = output_dict[
          'detection_classes'][0].astype(np.uint8)
      output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
      output_dict['detection_scores'] = output_dict['detection_scores'][0]
      if 'detection_masks' in output_dict:
        output_dict['detection_masks'] = output_dict['detection_masks'][0]
  return output_dict

def OCRMethod1(classNames,locations):
    airplaneName = IndentifyAirplaneName(classNames,locations)
    #import cv2
    #import numpy as np
    image=cv2.imread(image_path)    #döndürmek istediğim görüntünün bilgisayarımda ki konumunu belirtiyorum
    
    height, width = image.shape[:2]

    i=0
    for className in classNames:
      ymin, xmin, ymax, xmax = locations[i]
      start_row = ymin*1080
      end_row = ymax*1080
      start_col = xmin*1920
      end_col = xmax*1920

      cropped=image[start_row:end_row , start_col:end_col]

      cv2.imshow('Original Image', image)     #açılan pencerede ilk orjinal görüntümüz açılır
    
      cv2.waitKey(0)
    
      cv2.imshow('Cropped Image', cropped)   #çarpıya tıkladığımız da ise kırpılmış görüntü ile karşılaşırız
      cv2.waitKey(0)
      cv2.destroyAllWindows()
      i+=1
    

def OCRMethod(classNames,locations,image1):
  airplaneName = IndentifyAirplaneName(classNames,locations)  

  image=cv2.imread("test.jpg")    #döndürmek istediğim görüntünün bilgisayarımda ki konumunu belirtiyorum
  #cv2.imshow(' Image', image)
  if(airplaneName == "Airbus"):
    i=0
    for classname in classNames:
      if(classname[0].startswith('airspeed') or 1):

        ymin, xmin, ymax, xmax = locations[i]

        #height, width = image.shape[:2]

        start_row, start_col=int(ymin*1080),int(xmin*1920)    #kırpmak istediğiniz boyuta göre değerler verebilirsiniz
        end_row, end_col=int(ymax*1080),int(xmax*1920) 

        cropped=image[start_row:end_row , start_col:end_col]

        #cv2.imshow('Cropped Image', cropped)   #çarpıya tıkladığımız da ise kırpılmış görüntü ile karşılaşırız

        def len_asd(asd):            
          i = 0
          leng=len(asd)
          while (i < leng):
            if(ord(asd[i]) >= 48 and ord(asd[i]) <= 57):
              i = i +1
              continue

            else:
              print("Not a number")
              return 0
            i = i+1
          return 1
        
        
        reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
        result2 = reader.readtext(cropped, detail = 0)
        leng1 = len(result2)
        j = 0
        our_len = 0
        result3 = result2
        while (j < leng1):
          if(len_asd(result2[j])):
            result3[our_len] = result2[j]
            our_len = our_len + 1
          j = j+1
        result4 = result3[0:our_len]
        
        print("----------")
        print(result4)
        time.sleep(10)
      i+=1
    
    
    '''
    #import easyocr
    def len_asd(asd):
        
        i = 0
        print(asd)
        leng=len(asd)
        while (i < leng):
            if(ord(asd[i]) >= 48 and ord(asd[i]) <= 57):
                #print(asd[i])
                #print(ord(asd[i]))
                i = i +1
                continue
        		
            else:
                
                #print(asd[i])
                #print(ord(asd[i]))
                print("Not a number")
                return 0;
            i = i+1
        return 1
    
    
    #klm = ['asd3', 'asd2']
    k = 0
    while (k < 1):
            reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
            result = reader.readtext(cropped)
            
            
            result2 = reader.readtext(cropped, detail = 0)
            
            leng1 = len(result2)
            
            j = 0
            our_len = 0
            result3 = result2
            while (j < leng1):
                if(len_asd(result2[j])):
                    result3[our_len] = result2[j]
                    our_len = our_len + 1
                j = j+1
           
            result4 = result3[0:our_len-1]     
            k = k +1

  
  
'''

def IndentifyAirplaneName(classNames,locations):
  i=0
  for classname in classNames:
    if(classname[0].startswith('airspeed')):
      ymin, xmin, ymax, xmax = locations[i]
      if(ymax-ymin>0.65):
        return "Boeing"
      else:
        return "Airbus"
    i+=1
  return "Nothing"


image = Image.open(image_path)
# the array based representation of the image will be used later in order to prepare the
# result image with boxes and labels on it.
image_np = load_image_into_numpy_array(image)
# Expand dimensions since the model expects images to have shape: [1, None, None, 3]
image_np_expanded = np.expand_dims(image_np, axis=0)
# Actual detection.
output_dict = run_inference_for_single_image(image_np, detection_graph)
# Visualization of the results of a detection.
image__,classNames,locations = vis_util.visualize_boxes_and_labels_on_image_array(
  image_np,
  output_dict['detection_boxes'],
  output_dict['detection_classes'],
  output_dict['detection_scores'],
  category_index,
  instance_masks=output_dict.get('detection_masks'),
  use_normalized_coordinates=True,
  line_thickness=8)
plt.figure(figsize=IMAGE_SIZE)
plt.imsave('outputImage.jpg', image_np)
print("OCRMethod")
time.sleep(2)
try:
  OCRMethod(classNames,locations,image)
except Exception as e:
  print(e)
time.sleep(1000)





