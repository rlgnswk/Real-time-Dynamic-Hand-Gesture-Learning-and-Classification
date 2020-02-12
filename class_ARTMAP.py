# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 14:50:01 2020

@author: rlgns
"""

'''
HGU
CSEE
KGH

Fuzzy art + map
'''

import numpy as np
import os
import matplotlib.pyplot as plt



class Fuzzy_ARTMAP():
    # create the artmap
    def __init__(self, feature_space = 1, threshold = 0.5, w_list = [] , label_list = []):
        print("## ARTMAP model is created##")
        self.M = feature_space
        self.threshold = threshold
        self.w_list = w_list
        self.label_list = label_list
    #convert input to elementwise complement
    def complement_coding(self, input_vector):
        #normalization_vector(input_vector) 
        complement_vector = [1-i for i in input_vector]
        return complement_vector
    #concat the input and complemented input for artmap input
    def make_input_x(self, input_i):
        return input_i + self.complement_coding(input_i)
    
    #component_wise_min
    def component_wise_min(self, x,y):
        if len(x) != len(y):
            return print("vector length unmatched!")
        zip_list = list(zip(x,y))
        min_list = [min(i,j) for i,j in zip_list]
        return min_list
 
    # choice function #𝑇_𝑗=|x∧𝐰_𝑗 |+(1−𝛼)(2𝑀−|𝐰_𝑗 |)  (Choice by difference)
    def choice_function(self, x, w):
        #|𝐱∧𝐰_𝑗 |
        non_zero_a = 0.000001
        x_w = self.component_wise_min(x,w)
        x_w_norm = sum(x_w)
        w_norm = sum(w)
        #𝑇_𝑗=|x∧𝐰_𝑗 |+(1−𝛼)(2𝑀−|𝐰_𝑗 |)  범위가 0~2 인듯??
        T_j = x_w_norm + (1-non_zero_a)*(2*self.M - w_norm)
        return T_j    
    
    #find nearest w at input x
    def Code_competition(self, input_x, label):
        choice_list = [self.choice_function(input_x, w) for w in self.w_list]
        #print("choice list:", choice_list)
        #indices = [i for i, x in enumerate(t_list) if x == 1.0] # is the input in any categories?
        #if input belong to any w
        return self.template_matching(input_x, label, choice_list)

    #template matching the calculated value from input and template 
    def template_matching(self, input_x, label ,choice_list):  
        for idx, index in enumerate(np.flip(np.argsort(choice_list))): # sort the up-down and test each in order
            #|𝑅_𝐽⊕𝐈"|=𝑀−|𝐱∧𝐰_𝐽 |≤𝑀(1−𝜌)
            #print(self.w_list[index])
            x_w =self.component_wise_min(input_x , self.w_list[index])
            # matching template and label
            if self.label_list[index] == label:
                matching_bool = ((self.M - sum(x_w))<=(self.M-self.threshold))
                if matching_bool == True : # if matching is true, extend that w-th boundary 
                    self.w_list[index] = self.component_wise_min(input_x, self.w_list[index]) # template learning
                    #print("template learning",  self.w_list )
                    #print("Related template:", self.w_list[index]  )
                    #print("Related label:", self.label_list[index]  )
                    return self.w_list, self.label_list[index]
                
        # if any boundary is unmatched, make new boundary by input_x
        self.w_list = self.w_list + [input_x] # Category addition
        self.label_list = self.label_list + [label]
        #print("Category addition", self.w_list)
        #print("additional label:", label)
        return  self.w_list, label
    
    # train mode / add or expanding the templates b input
    def Train(self, input_i ,label):
        input_x = self.make_input_x(input_i)
        self.w_list, category  = self.Code_competition(input_x, label)
        return category

    # test mode / return the label or None by input
    def Test(self, input_i):
        input_x = self.make_input_x(input_i)
        # select max choice Function value
        choice_list = [self.choice_function(input_x, w) for w in self.w_list]

        return self.label_list[choice_list.index(max(choice_list))]

        
        
    # print the information of the ARTMAP
    def info(self):
        print("feature space = ", self.M)
        print("threshold = ", self.threshold)
        print("w_list =", self.w_list)
        print("label_list: = ", self.label_list)
        print("num of categories:", len(self.w_list)) 
        
    def plot_ART(self):
        pass   
    # Reset the ARTMAP elements   
    def Reset(self):
        self.w_list = []
        self.label_list = []
        return print("Reset the all of templates and labels")
    # save the label list and w list
    def Save(self, path = os.getcwd()):
        #np_label = np.asarray(self.label_list)
        #np_w = np.asarray(self.w_list)
        np.save(path+"\\label_info.npy",self.label_list)
        np.save(path+"\\template_info.npy",self.w_list)        
    # load the label list and w list    
    def Load(self, path = os.getcwd()):
        self.label_list = np.load(path+"\\label_info.npy").tolist()
        self.w_list = np.load(path+"\\template_info.npy").tolist()
