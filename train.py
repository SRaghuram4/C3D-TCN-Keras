import numpy as np
import warnings
import threading
import os
from keras.callbacks import ReduceLROnPlateau
import sklearn
from sklearn import cross_validation
import matplotlib.pyplot as plt
from functools import partial
import itertools

import keras
from keras.models import Sequential, Model
from keras.layers import Input, Dense, TimeDistributed, merge, Lambda
from keras.layers.core import *
from keras.layers.convolutional import *
from keras.layers.recurrent import *
from keras.regularizers import l2,l1
from keras.layers.normalization import BatchNormalization
import tensorflow as tf
from keras import backend as K
from keras.utils import np_utils
from keras import optimizers
from keras.activations import relu
from keras.utils import np_utils
from keras.optimizers import RMSprop,SGD,Adam
from keras.callbacks import ModelCheckpoint
from keras.layers.merge import add,concatenate
from keras.models import load_model

warnings.filterwarnings("ignore")

machine ='ye_home'

# Path to the directories of features and labels
if machine == 'ye_home':
	path = '/home/ye/Works'
elif machine == 'MARCC':
	path = '/home-4/ytian27@jhu.edu/scratch/yetian'

VGG_train01_dir = os.path.join('/media/ye/youtube-8/UCF101-VGG-SPLIT/trainlist01')
VGG_train02_dir = os.path.join('/media/ye/youtube-8/UCF101-VGG-SPLIT/trainlist02')
VGG_train03_dir = os.path.join('/media/ye/youtube-8/UCF101-VGG-SPLIT/trainlist03')
VGG_test01_dir = os.path.join('/media/ye/youtube-8/UCF101-VGG-SPLIT/testlist01')
VGG_test02_dir = os.path.join('/media/ye/youtube-8/UCF101-VGG-SPLIT/testlist02')
VGG_test03_dir = os.path.join('/media/ye/youtube-8/UCF101-VGG-SPLIT/testlist03')
# VGG_train01_dir = os.path.join(path, 'C3D-TCN-Keras/features/VGG-split/trainlist01')
# VGG_train02_dir = os.path.join(path, 'C3D-TCN-Keras/features/VGG-split/trainlist02')
# VGG_train03_dir = os.path.join(path, 'C3D-TCN-Keras/features/VGG-split/trainlist03')
# VGG_test01_dir = os.path.join(path, 'C3D-TCN-Keras/features/VGG-split/testlist01')
# VGG_test02_dir = os.path.join(path, 'C3D-TCN-Keras/features/VGG-split/testlist02')
# VGG_test03_dir = os.path.join(path, 'C3D-TCN-Keras/features/VGG-split/testlist03')
C3D_train01_dir = os.path.join(path, 'C3D-TCN-Keras/features/C3D-split/trainlist01')
C3D_train02_dir = os.path.join(path, 'C3D-TCN-Keras/features/C3D-split/trainlist02')
C3D_train03_dir = os.path.join(path, 'C3D-TCN-Keras/features/C3D-split/trainlist03')
C3D_test01_dir = os.path.join(path, 'C3D-TCN-Keras/features/C3D-split/testlist01')
C3D_test02_dir = os.path.join(path, 'C3D-TCN-Keras/features/C3D-split/testlist02')
C3D_test03_dir = os.path.join(path, 'C3D-TCN-Keras/features/C3D-split/testlist03')
C3D_dir = os.path.join(path, 'C3D-TCN-Keras/features/C3D')
VGG_dir = os.path.join(path, 'C3D-TCN-Keras/features/VGG')
label_dir = os.path.join(path, 'C3D-TCN-Keras/classInd.txt')

#######################################################################
# TCN models
def TK_TCN_resnet(
					 n_classes, 
					 feat_dim,
					 max_len,
					 art,
					 gap=1,
					 dropout=0.0,
					 activation="relu"):
	"""Reviced TK'S TCN model. num_block = 2. initial_conv_num=64.
	Args:
		n_classes: number of classes for this kind of label.
		feat_dim: the dumention of the feature.
		max_len: the number of frames for each video.
	Returns:
		model: uncompiled model."""


	if K.image_dim_ordering() == 'tf':
		ROW_AXIS = 1
		CHANNEL_AXIS = 2
	else:
		ROW_AXIS = 2
		CHANNEL_AXIS = 1

	if art == 'V1':
		initial_stride = 1
		initial_filter_dim = 4
		initial_num = 64	 
		config = [ 
							 [(1,4,64)],
							 [(1,4,64)],
							 [(1,4,64)],
							 [(2,4,128)],
							 [(1,4,128)],
							 [(1,4,128)],
							 [(2,4,256)],
							 [(1,4,256)],
							 [(1,4,256)]
						 ]
	elif art == 'V2':
		initial_stride = 1
		initial_filter_dim = 2
		initial_num = 256	 
		config = [ 
							 [(1,2,initial_num)],
							 [(1,2,initial_num)],
							 [(2,2,initial_num*2)],
							 [(1,2,initial_num*2)],

						 ]
	elif art == 'V3':
		initial_stride = 1
		initial_filter_dim = 4
		initial_num = 128	 
		config = [ 
							 [(1,4,initial_num)],
							 [(1,4,initial_num)],
							 [(2,4,initial_num*2)],
							 [(1,4,initial_num*2)],
						 ]
	elif art == 'V4':
		initial_stride = 1
		initial_filter_dim = 4
		initial_num = 64	 
		config = [ 
							 [(1,4,initial_num)],
							 [(1,4,initial_num)],
							 [(2,4,initial_num*2)],
							 [(1,4,initial_num*2)],
							 [(2,4,initial_num*4)],
							 [(1,4,initial_num*4)],
						 ]
	elif art == 'V5':
		initial_stride = 1
		initial_filter_dim = 4
		initial_num = 64	 
		config = [ 
							 [(1,4,initial_num)],
							 [(1,4,initial_num)],
							 [(1,4,initial_num)],
							 [(1,4,initial_num)],
							 [(2,4,initial_num*2)],
							 [(1,4,initial_num*2)],
							 [(1,4,initial_num*2)],
							 [(1,4,initial_num*2)],
							 [(2,4,initial_num*4)],
							 [(1,4,initial_num*4)],
							 [(1,4,initial_num*4)],
							 [(1,4,initial_num*4)],
						 ]
	elif art == 'V6':
		initial_stride = 1
		initial_filter_dim = 6
		initial_num = 64	 
		config = [ 
							 [(1,6,initial_num)],
							 [(1,6,initial_num)],
							 [(1,6,initial_num)],
							 [(2,6,initial_num*2)],
							 [(1,6,initial_num*2)],
							 [(1,6,initial_num*2)],
							 [(2,6,initial_num*4)],
							 [(1,6,initial_num*4)],
							 [(1,6,initial_num*4)],
						 ]
	elif art == 'V7':
		initial_stride = 1
		initial_filter_dim = 3
		initial_num = 64	 
		config = [ 
							 [(1,3,initial_num)],
							 [(1,3,initial_num)],
							 [(1,3,initial_num)],
							 [(2,3,initial_num*2)],
							 [(1,3,initial_num*2)],
							 [(1,3,initial_num*2)],
							 [(2,3,initial_num*4)],
							 [(1,3,initial_num*4)],
							 [(1,3,initial_num*4)],
						 ]


	input = Input(shape=(max_len,feat_dim))
	model = input

	model = Conv1D(initial_num, 
								 initial_filter_dim,
								 strides=initial_stride,
								 padding="same",
								 kernel_initializer="he_normal")(model)

	for depth in range(0,len(config)):
		for stride,filter_dim,num in config[depth]:
			bn = BatchNormalization(axis=CHANNEL_AXIS)(model)
			relu = Activation(activation)(bn)
			dr = Dropout(dropout)(relu)
			res = Conv1D(num, 
									 filter_dim,
									 strides=stride,
									 padding="same",
									 kernel_initializer="he_normal")(dr)

			res_shape = K.int_shape(res)
			model_shape = K.int_shape(model)
			if res_shape[CHANNEL_AXIS] != model_shape[CHANNEL_AXIS]:
				model = Conv1D(num, 
											 1,
											 strides=stride,
											 padding="same",
											 kernel_initializer="he_normal")(model)

			model = add([model,res])

	bn = BatchNormalization(axis=CHANNEL_AXIS)(model)
	model = Activation(activation)(bn)

	if gap:
		pool_window_shape = K.int_shape(model)
		gap = AveragePooling1D(pool_window_shape[ROW_AXIS],
													 strides=1)(model)
		flatten = Flatten()(gap)
	else:
		flatten = Flatten()(model)
	dense = Dense(units=n_classes, 
								activation="softmax",
								kernel_initializer="he_normal")(flatten)

	model = Model(inputs=input, outputs=dense)
	return model

######################################################################################################
def trans_label(txt):
	# label_list = np.loadtxt(txt)
	label_list = np.genfromtxt(txt, delimiter=' ', dtype=None)
	label_dict = {}
	# num_lab = len(label_list)
	num_lab = 101
	for i in range(num_lab):
		# print label_list[i][1], label_list[i][0]
		label_dict[label_list[i][1]] = label_list[i][0]
	# print label_dict['HandStandPushups']
	return label_dict

#####################################################################################################
def to_vector(mat):
	"""Convert categorical data into vector.
	Args:
		mat: onr-hot categorical data.
	Returns:
		out2: vectorized data."""
	out = np.zeros((mat.shape[0],mat.shape[1]))
	out2 = np.zeros((mat.shape[0]))
	for i in range(mat.shape[0]):
		for n, j in enumerate(mat[i]):
			if j == np.amax(mat[i]):
				out[i][n] = 1
				out2[i] = n

	return out2
#####################################################################################################
class Iterator(object):
	def __init__(self, N, batch_size, shuffle, seed):
		self.N = N
		self.batch_size = batch_size
		self.shuffle = shuffle
		self.batch_index = 0
		self.total_batches_seen = 0

	def __iter__(self):
		return self

	def __next__(self, *args, **kwargs):
		return self.next(*args, **kwargs)

######################################################################################################
class VideoIterator(Iterator):
	def __init__(
		self, 
		data_generator, 
		video_files,
		max_sequence_len,
		nb_classes,
		cache_dir,
		batch_size, 
		shuffle=False, 
		seed=None):

		self.data_generator = data_generator
		self.video_files = video_files
		self.nVideos = len(self.video_files)

		self.cache_dir = cache_dir

		self.max_sequence_len = max_sequence_len
		self.nb_classes = nb_classes
		self.batch_size = batch_size

		self.vid_size_cache = {}
		self.label_dict = trans_label(label_dir)

		# The input sequence consists of concatenated video clips, up to a maximum length of self.max_sequence_len:
		self.Xtrain = np.zeros((self.batch_size,self.max_sequence_len,4096), dtype=np.float32)

		# The output is a frame-level segmentation (one-hot labeling, per-frame for the entire sequence)
		self.ytrain = np.zeros((self.batch_size,self.nb_classes), dtype=np.float32)

		self.ji = 0

	def next(self):
		"""
		do the work here
		"""

		# Initialize the input sequence batch of features to all 0's initially
		self.Xtrain[:] = 0.0

		# Initialize the output sequence batch of labels to all 0's initially
		self.ytrain[:] = 0.0

		# Construct a batch to update the training
		b = 0

		ji = self.ji

		while b < self.batch_size:
			# Randomly permute the video file order
			# Keep filling in frames from video clips until the buffer is full
			start = 0
			break_out = False
			while True:
				if break_out:
					break
				if ji > self.nVideos-1:
					self.ji = 0
					ji = 0

				vid_file0 = self.video_files[ji]
				
				# if not os.path.exists(vid_file0):
				# 	# ji += 1
				# 	break

				feature = np.load(os.path.join(self.cache_dir,vid_file0))
				# print feature.shape
				n_frames0 = feature.shape[0]

				# Retrieve the cached video features 
				label0 = self.label_dict[vid_file0[:-12]] -1
				# print 'label0', label0
			
				# Now concatenate this sequence to the end of this batch
				end = start + n_frames0
				if end > self.max_sequence_len:
					end = self.max_sequence_len
					n_frames0 = end-start
					break_out = True
				self.Xtrain[b,start:end] = feature[:n_frames0]

				# Store the labels for these frames
				self.ytrain[b,label0] = 1.0   

				start = end  # update for next sequence   
				ji += 1       

			
			# And increment the batch index
			b += 1

		self.ji = ji

		return self.Xtrain, self.ytrain



####################################################################################################
class MyDataGenerator(object):
	def __init__(self, video_files, max_sequence_len, nb_classes, cache_dir):
		self.video_files = video_files
		self.max_sequence_len = max_sequence_len
		self.nb_classes = nb_classes
		self.cache_dir = cache_dir

	def flow(self, batch_size):
		return VideoIterator(
			self, 
			self.video_files,
			self.max_sequence_len,
			self.nb_classes,
			self.cache_dir,
			batch_size=batch_size)


########################################################################################################
def train_model(max_len, feature, art):
	"""Load data, compile, fit, evaluate model, and predict labels.
	Args:
		model: model name.
		y_categorical: whether to use the original label or one-hot label. True for classification models. False for regression models.
		max_len: the number of frames for each video.
		get_cross_validation: whether to cross validate. 
		non_zero: whether to use the non-zero data. If true 
	Returns:
		loss_mean: loss for this model.
		acc_mean: accuracy for classification model.
		classes: predications. Predication for all the videos is using cross validation.
		y_test: test ground truth. Equal to all labels if using cross validation."""

	n_classes = 101
	if feature == 'C3D01':
		train_dir = C3D_train01_dir
		test_dir = C3D_test01_dir
	elif feature == 'C3D02':
		train_dir = C3D_train02_dir
		test_dir = C3D_test02_dir
	elif feature == 'C3D03':
		train_dir = C3D_train03_dir
		test_dir = C3D_test03_dir
	elif feature == 'VGG01':
		train_dir = VGG_train01_dir
		test_dir = VGG_test01_dir
	elif feature == 'VGG02':
		train_dir = VGG_train02_dir
		test_dir = VGG_test02_dir
	elif feature == 'VGG03':
		train_dir = VGG_train03_dir
		test_dir = VGG_test03_dir
	elif feature == 'VGG':
		train_dir = VGG_dir
		test_dir = VGG_dir
	elif feature == 'C3D':
		train_dir = C3D_dir
		test_dir = C3D_dir

	if train_dir == test_dir:
		files = os.listdir(train_dir)
		train_files = files[0:10000]
		val_files = files[10001:]
	else:
		train_files = os.listdir(train_dir)
		val_files = os.listdir(test_dir)


	# choose model

	model = TK_TCN_resnet(n_classes=n_classes, feat_dim=4096, max_len=max_len, art=art)
	# compile model
	optimizer = Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
	# optimizer = SGD(lr=0.01, momentum=0.9, decay=0.0, nesterov=True)
	model.compile(loss='categorical_crossentropy', optimizer=optimizer,metrics=['accuracy'])
	# model.compile(loss='mean_absolute_error', optimizer=optimizer,metrics=['categorical_accuracy'])
	# visualize
	# model.summary()

		# Setup the data generator--first for training

	# print train_files, len(train_files)
	datagenT = MyDataGenerator(video_files=train_files,
		max_sequence_len=max_len,
		nb_classes=n_classes,
		cache_dir=train_dir)

	# # Then make a validation generator
	datagenV = MyDataGenerator(video_files=val_files,
		max_sequence_len=max_len,
		nb_classes=n_classes,
		cache_dir=test_dir)

	# nb_epoch = 50
	# batch_size = 32
	# samples_per_epoch = batch_size*3125
	nb_epoch = 100
	batch_size = 10
	samples_per_epoch = 10000/batch_size +1

	#checkpointer = ModelCheckpoint(out_model_file, monitor='loss', verbose=0, save_best_only=True, mode='auto')
	# checkpointer = ModelCheckpoint(out_model_file, monitor='acc', verbose=0, save_best_only=True, mode='auto')
	model.fit_generator(datagenT.flow(batch_size=batch_size), 
		nb_epoch=nb_epoch, 
		samples_per_epoch=samples_per_epoch, 
		verbose=1)

	loss, acc = model.evaluate_generator(datagenV.flow(batch_size=10), 3000/batch_size +1)
	model.save('VGG_TCN_model.h5')
	print loss, acc
	return loss, acc

if __name__ == '__main__':
	# max_len = 80
	# print 'v1'
	# loss1, acc1 = train_model(max_len, feature='VGG01',art='V1')
	# print ''
	# max_len = 80
	# print 'v2'
	# loss2, acc2 = train_model(max_len, feature='VGG01',art='V2')
	# print ''
	# max_len = 80
	# print 'v3'
	# loss3, acc3 = train_model(max_len, feature='VGG',art='V3')
	# max_len = 80
	# print 'v4'
	# loss4, acc4 = train_model(max_len, feature='VGG01',art='V4')
	# print ''
	# max_len = 80
	# print 'v5'
	# loss5, acc5 = train_model(max_len, feature='VGG01',art='V5')
	# print ''
	# max_len = 80
	# print 'v6'
	# loss6, acc6 = train_model(max_len, feature='VGG01',art='V6')
	# max_len = 80
	# print 'v7'
	# loss7, acc7 = train_model(max_len, feature='VGG01',art='V7')


	# max_len = 60
	# print '60'
	# loss8, acc8 = train_model(max_len, feature='VGG01',art='V3')
	# max_len = 100
	# print '100'
	# loss9, acc9 = train_model(max_len, feature='VGG01',art='V3')
	# max_len = 120
	# print '120'
	# loss10, acc10= train_model(max_len, feature='VGG01',art='V3')

	# print acc1, acc2, acc3, acc4, acc5, acc6, acc7, acc8, acc9, acc10

	train_dir = VGG_train02_dir
	test_dir = VGG_test02_dir
	val_files = os.listdir(test_dir)
	model  = load_model('VGG_TCN_model.h5')
	batch_size = 10
	datagenV = MyDataGenerator(video_files=val_files,
		max_sequence_len=80,
		nb_classes=101,
		cache_dir=test_dir)
	loss, acc = model.evaluate_generator(datagenV.flow(batch_size=10), 3000/batch_size +1)
	print loss, acc