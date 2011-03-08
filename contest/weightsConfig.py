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
                'attackModule_distanceToEnemies'   : 2,  \

                'defenseModule_maxMinOrZero' : -10, \
                'defenseModule_maxMin' : -5, \
                'defenseModule_avgMin' : -5, \
                'defenseModule_avgAvgDistances' : -.3, \
                'defenseModule_averageThreat' : -13, \
                'defenseModule_safeFood' : 3,\
                'defenseModule_lackDefenders':-3, \

                'ourAgent_hltWeight': .5, \
                'ourAgent_dWeight' : .5, \
                'ourAgent_attackWeight' : .01, \
                'ourAgent_canBeAttackingThreshold' : 5, \
                'ourAgent_theyCanBeAttackingThreshold' : 5, \

                'hltAgent_ourAverageDistanceToSquares' : -2, \
                'hltAgent_averageInactivity' : -40000, \
                'hltAgent_opponentMax' : -5, \
                'hltAgent_secondMax' : -2, \
                'hltAgent_zerosecondMax' : -2, \
                'hltAgent_ourMaxDistance' : -1, \
                'hltAgent_teamavgMinDistanceToEdge' : -2, \
                'hltAgent_lackHLT' : -3, \
              }

# Map to specify the range that our weights can be in (bound as closely
# as you can for values that will vary widely, such as exponents)

WeightsRangeMap = { \
                    'attackModule_foodEatenReward'     : (-1000, 1000), \
                    'attackModule_nearestFoodPower'    : (1, 2),  \
                    'attackModule_nearestFoodCoeff'    : (-10, 10),  \
                    'attackModule_totalFoodCoeff'      : (-10, 10),  \
                    'attackModule_distanceApartReward' : (-10, 10),  \
                    'attackModule_distanceToEnemies'   : (-10, 10),  \

                    'defenseModule_maxMinOrZero' : (-100,100), \
                    'defenseModule_maxMin' : (-100,100), \
                    'defenseModule_avgMin' : (-100,100), \
                    'defenseModule_avgAvgDistances' : (-100,100), \
                    'defenseModule_averageThreat' : (-100, 100),\
                    'defenseModule_safeFood' : (-100,100),\
                    'defenseModule_lackDefenders': (-50,50),\

                    'ourAgent_hltWeight': (0,1), \
                    'ourAgent_dWeight' : (0,1), \
                    'ourAgent_attackWeight' : (0,1), \
                    'ourAgent_canBeAttackingThreshold' : (0,20), \
                    'ourAgent_theyCanBeAttackingThreshold' : (0,20), \

                    'hltAgent_ourAverageDistanceToSquares' : (-10,5), \
                    'hltAgent_averageInactivity' : (-10,5), \
                    'hltAgent_opponentMax' : (-10,5), \
                    'hltAgent_secondMax' : (-10,5), \
                    'hltAgent_zerosecondMax' : (-10,5), \
                    'hltAgent_ourMaxDistance' : (-10,5), \
                    'hltAgent_teamavgMinDistanceToEdge' : (-10,5), \
                    'hltAgent_lackHLT' : (-100,100), \
                  }
