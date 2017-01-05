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
from __future__ import print_function
from pyspark.sql import SparkSession
    spark = SparkSession\
        .builder\
        .appName("LinearRegressionWithElasticNet")\
        .getOrCreate()

df = spark.read.load("/home/augustinus/Downloads/sample.csv", format="csv",header='true')
df=df.filter(df.Total_amount>0)
training=df.selectExpr("Total_amount as price","Trip_distance as distance","Passenger_count as pc")
training=training.select(training.price.cast("double"),training.distance.cast("double"),training.pc.cast("double"))

vecAssembler = VectorAssembler(inputCols=["distance", "pc"], outputCol="features")
#vecAssembler.transform(training).head().features
training=vecAssembler.transform(training)

lr = LinearRegression(maxIter=10, regParam=0.3, elasticNetParam=0.8)

lrModel = lr.fit(training)

# Print the coefficients and intercept for linear regression
print("Coefficients: " + str(lrModel.coefficients))
print("Intercept: " + str(lrModel.intercept))
spark.stop()


