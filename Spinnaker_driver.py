# coding=utf-8
# =============================================================================
# Copyright (c) 2001-2021 FLIR Systems, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
#
# Acquisition.py shows how to acquire images. It relies on
# information provided in the Enumeration example. Also, check out the
# ExceptionHandling and NodeMapInfo examples if you haven't already.
# ExceptionHandling shows the handling of standard and Spinnaker exceptions
# while NodeMapInfo explores retrieving information from various node types.
#
# This example touches on the preparation and cleanup of a camera just before
# and just after the acquisition of images. Image retrieval and conversion,
# grabbing image data, and saving images are all covered as well.
#
# Once comfortable with Acquisition, we suggest checking out
# AcquisitionMultipleCamera, NodeMapCallback, or SaveToAvi.
# AcquisitionMultipleCamera demonstrates simultaneously acquiring images from
# a number of cameras, NodeMapCallback serves as a good introduction to
# programming with callbacks and events, and SaveToAvi exhibits video creation.

import os
import PySpin
import sys
import numpy as np



class myCamera:
    def __init__(self,num=0):
        self.system = PySpin.System.GetInstance()
        system = self.system
        # Get current library version
        version = system.GetLibraryVersion()
        print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))
        cam_list = system.GetCameras()
        print(cam_list)
        self.num = num
    def connect(self):
        cam_list = self.system.GetCameras()
        system = self.system
        num_cameras = cam_list.GetSize()
        self.cam = cam_list[self.num]
        self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()

        # Initialize camera
        self.cam.Init()

        # Retrieve GenICam nodemap
        self.nodemap = self.cam.GetNodeMap()
        
        try:
            node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            # Retrieve entry node from enumeration node
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False

            # Retrieve integer value from entry node
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

            print('Acquisition mode set to continuous...')

            #  Begin acquiring images
            #
            #  *** NOTES ***
            #  What happens when the camera begins acquiring images depends on the
            #  acquisition mode. Single frame captures only a single image, multi
            #  frame catures a set number of images, and continuous captures a
            #  continuous stream of images.
            #
            #  *** LATER ***
            #  Image acquisition must be ended when no more images are needed.
            self.cam.BeginAcquisition()



        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

    def getGreyscale(self):
        image_result = self.cam.GetNextImage(1000)
        image_data = image_result.GetNDArray()
        image_result.Release()
        return image_data

    def getHighResolution(self,tacq=1):
        try:
            image_result = self.cam.GetNextImage(1000)
            vid_gray = image_result.GetNDArray()
            image_result.Release()
            error = False
        except:
            error = True
        return vid_gray, error