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
import argparse

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

def OCRMethod(classNames,locations,image1):
  airplaneName = IndentifyAirplaneName(classNames,locations)
  airSpeed=0
  altimeter=0  
  horizontalSituation=0
  verticalSpeed=0
  image=cv2.imread("test.jpg")
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  i=0
  for classname in classNames:
    ymin, xmin, ymax, xmax = locations[i]
    start_row, start_col=int(ymin*1080),int(xmin*1920)  
    end_row, end_col=int(ymax*1080),int(xmax*1920) 
    cropped=image[start_row:end_row , start_col:end_col]

    cv2.imshow(classname[0], cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))   
    cv2.waitKey(0)
    ## ------ OCR  -----------

    result4 = OCRResult(cropped)
    
    if classname[0].startswith('verticalSpeed')  and airplaneName == "Airbus":
      start_rowDown = end_rowUp = int(end_row - (end_row-start_row)/2 )
      croppedUp = image[start_row:end_rowUp,start_col-10:end_col]
      croppedDown = image[start_rowDown:end_row,start_col-10:end_col]
      resultUp = OCRResult(croppedUp)
      
      resultDown = OCRResult(croppedDown)
      control_9 = 0
      d_9 = 0
      if len(resultUp) < 4:
        while d_9 < len(resultUp):
          if len(str(resultUp[d_9])) >= 2:
            control_9 = 1
            break 
          d_9+=1
      else:
        control_9 = 1

      if control_9 == 1:
        croppedUp = image[start_row:end_rowUp,start_col+30:end_col]
        resultUp = OCRResult(croppedUp)
        result4 = resultUp
      else:
        croppedDown = image[start_rowDown:end_row,start_col+30:end_col]
        resultDown = OCRResult(croppedDown)
        result4 = resultDown
      
    
    
    

    if len(result4)> 0:
      # Airspeed
      if(classname[0].startswith('airspeed') and airplaneName == "Airbus"):
        if len(result4) <= 3:
          airSpeed = 0

        elif len(result4) == 4:
          if abs(result4[-1]-result4[-2]) == 20:
            airSpeed = result4[-2] + 10
          elif abs(result4[-3]-result4[-2]) == 20:
            airSpeed = result4[-2] + 10
          else:
            airSpeed = -1

        elif len(result4) == 5:
          if (result4[-3]-result4[-2])==20:
            airSpeed = result4[-3]
          elif (result4[0]-result4[1]) == 20:
            airSpeed = result4[0] - 40
          else:
            airSpeed = -1
      # altimeter
      elif(classname[0].startswith('altimeter') and airplaneName == "Airbus"):
        cropped = image[535:573,1225:1310]
        result4_100 = OCRResult(cropped)
        cropped = image[510:600,1310:1352]
        result4 = OCRResult(cropped)
        if len(result4)>2 and (result4[0] - result4[1]) == 20:
          altimeter=int(result4_100[0]*100+result4[1])
        elif len(result4)>2 and (result4[0] - result4[2]) == 40:
          altimeter=int(result4_100[0]*100+result4[0]-20)
        else:
          for result_Altimeter in result4:
            if (result_Altimeter>9):
              altimeter = result4_100[0]*100 + result_Altimeter
      # horizontalSituation
      elif(classname[0].startswith('horizontalSituation') and airplaneName == "Airbus"):
        if len(result4) == 5:
          horizontalSituation = result4[2]
        elif len(result4) == 6:
          horizontalSituation = (result4[2] + result4[3])/2
      # verticalSpeed
      elif(classname[0].startswith('verticalSpeed') and airplaneName == "Airbus"): 
        if len(result4) > 0:
          if control_9 == 1:
            verticalSpeed = result4[0]*100
          else: 
            verticalSpeed = result4[0]*(-100)
        else:
          verticalSpeed = 0


      if(classname[0].startswith('airspeed') and airplaneName == "Boeing"):
        cropped = image[520:570,458:513]
        result4_1 = OCRResult(cropped)
        cropped = image[505:585,513:540]
        result4_2 = OCRResult(cropped)
        if len(result4_1) == 0:
          airSpeed=0
        elif len(result4_2) == 0:
          airSpeed = result4_1[0]*10
        elif len(result4_2) > 0:
          airSpeed = result4_1[0]*10 + result4_2[0]
          
      elif(classname[0].startswith('altimeter') and airplaneName == "Boeing"):
        
        cropped = image[521:567,1229:1354]
        result4_100 = OCRResult(cropped)
        cropped = image[496:589,1354:1400]
        result4 = OCRResult(cropped)
        if len(result4)>2 and (result4[0] - result4[1]) == 20:
          altimeter=int(result4_100[0]*100+result4[1])
        elif len(result4)>2 and (result4[0] - result4[2]) == 40:
          altimeter=int(result4_100[0]*100+result4[0]-20)
        else:
          for result_Altimeter in result4:
            if (result_Altimeter>9):
              altimeter = result4_100[0]*100 + result_Altimeter

      elif(classname[0].startswith('horizontalSituation') and airplaneName == "Boeing"):
        if len(result4) > 1:
          horizontalSituation = result4[1]
        elif len(result4) > 0:
          horizontalSituation = result4[0]
      elif(classname[0].startswith('verticalSpeed') and airplaneName == "Boeing"): 
        cropped = image[230:263,1369:1460]
        result4_Up = OCRResult(cropped)
        cropped = image[832:863,1369:1460]
        result4_Down = OCRResult(cropped)
        if len(result4_Up) > 0:
          verticalSpeed = result4_Up[0]
        elif len(result4_Down) > 0:
          verticalSpeed = -result4_Down[0]
        else:
          verticalSpeed = 0


    i+=1

  with open('OCRExport.txt', 'w') as f:
    f.write("airplaneName:"+str(airplaneName)+"\n")
    f.write("airSpeed:"+str(airSpeed)+"\n")
    f.write("altimeter:"+str(altimeter)+"\n")
    f.write("horizontalSituation:"+str(horizontalSituation)+"\n")
    f.write("verticalSpeed:"+str(verticalSpeed))
    f.close()



def lengthOCR(asd):            
  i = 0
  leng=len(asd)
  while (i < leng):
    if(ord(asd[i]) >= 48 and ord(asd[i]) <= 57):
      i = i +1
      continue

    else:
      return 0
      i = i+1
  return 1

def OCRResult(cropped):
  reader = easyocr.Reader(['ch_sim','en']) 
  result2 = reader.readtext(cropped, detail = 0)
  leng1 = len(result2)
  j = 0
  our_len = 0
  result3 = result2
  while (j < leng1):
    if(lengthOCR(result2[j])):
      result3[our_len] = result2[j]
      our_len = our_len + 1
    j = j+1
  result4 = result3[0:our_len]
      
  resultTemp = []
  for result in result4:
    try:
      resultTemp.append(int(result))
    except:
      _ = result
  result4 = resultTemp

  return result4

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

OCRMethod(classNames,locations,image)






