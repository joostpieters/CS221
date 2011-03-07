# weightsConfig.py

"""
-----------------------
  Weight Configuration
-----------------------

This file contains a dictionary used to weight modules, so they can presumably be
machine optimized.

"""

# Map of weights we plan to use to determine a policy

WeightsMap = { \
                'attackModule_foodEatenReward' : 1000, \
                'attackModule_nearestFoodPower' : 1.5, \
                'attackModule_nearestFoodCoeff' : 1,  \
                'attackModule_totalFoodCoeff'      : 1,  \
                'attackModule_distanceApartReward' : 5,  \
                'attackModule_distanceToEnemies'   : 2  \
              }

# Map to specify the range that our weights can be in (bound as closely
# as you can for values that will vary widely, such as exponents)

WeightsRangeMap = { \
                    'attackModule_foodEatenReward'     : (-1000, 1000), \
                    'attackModule_nearestFoodPower'    : (1, 2),  \
                    'attackModule_nearestFoodCoeff'    : (-10, 10),  \
                    'attackModule_totalFoodCoeff'      : (-10, 10),  \
                    'attackModule_distanceApartReward' : (-10, 10),  \
                    'attackModule_distanceToEnemies'   : (-10, 10)  \
                   }