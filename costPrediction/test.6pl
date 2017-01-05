#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 14:00:08 2016

@author: augustinus
"""
#import pyspark
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline

df = spark.read.load("/home/augustinus/Downloads/sample.csv", format="csv",header='true')
df=df.filter(df.Total_amount>0)
training=df.selectExpr("Total_amount as price","Trip_distance as distance","Passenger_count as pc")
training=training.select(training.price.cast("double"),training.distance.cast("double"),training.pc.cast("double"))

vecAssembler = VectorAssembler(inputCols=["distance", "pc"], outputCol="features")
#vecAssembler.transform(training).head().features
#vecAssembler.transform(training)

lr = LinearRegression(maxIter=100, regParam=0.3, elasticNetParam=0.8,labelCol="price",featuresCol="features")

# Fit the model
pipeline = Pipeline(stages=[vecAssembler,lr])
linearmodel = pipeline.fit(training)
predictions = linearmodel.transform(training)
#save model
linearmodel.save('output_Model')

# Select example rows to display.
predictions.select("prediction", "indexedLabel", "features").show(5)
spark.stop()
#ignore = ['id', 'label', 'binomial_label']
#assembler = VectorAssembler(
#    inputCols=[x for x in df.columns if x not in ignore],
#    outputCol='features')


