# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 18:33:27 2020

@author: windows
"""

class Parent:
    def __init__(self,name,age):
        self.name = name
        self.age = age
        
    def pritpp(self):
        print(self.name,self.age)
        
        
class Student(Parent):
    def __init__(self,name,age):
        super().__init__(name,age)
    

x = Student("raunak", 10)
x.pritpp()