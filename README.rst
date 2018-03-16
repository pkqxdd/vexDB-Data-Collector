:Author: Jerry Wang
:Date: Mar 16, 2017

General Information
===================

This repository includes script for collecting information of a VRC event from vexDB, primarily for better scouting. There are two different versions of script, one is synchronous and another is asynchronous. The asynchronous version should run a lot faster than the synchronous version, especially with slow Internet connection. However, if you are get any weird errors, try to run the synchronous version, as it is tested more. 

Dependencies
============

- aiohttp (only if you are running the asynchronous module)
- requests

To install all dependencies, including optional dependencies recommended by aiohttp, run

.. code:: sh
	
	sudo -H python3.6 -m pip install --upgrade requests aiohttp cchardet aiodns
	

Usage
=====

.. code:: sh

	python3.6 vexDB_data_collector.py [Event Code] [Output Path]`

Or, if you are running the asynchronous version

.. code:: sh

	python3.6 vexDB_data_collector_async.py [Event Code] [Output Path]

Arguments
---------

:Event Code: Optional, identifier of the vex event. It should be in format of ``RE-VRC-YY-XXXX``. Default to ``RE-VRC-17-3805``, the event code for 2018 VEX Robotics World Championship High School Division. You can find it on robotevents.com for a specific event. 
:Output Path: Optional, path for the CSV file output. Default to ``/path/to/script/event-name data.csv``

Sample Output
=============

Below is sample output of first five lines of output of

 .. code:: sh

 	python3.6 vexDB_data_collector_async.py RE-VRC-17-4151

Note that the file will be in arbitrary order if you are running the asynchronous version. You can always sort the file based on individual columns using program such as Microsoft Excel. 

.. csv-table::
	:header: Team Number,Team Name,Organization,Region,Country,Autonomous Skill,Autonomous Rank,Driver Skill,Driver Rank,Combined Skills,Skill Rank,vRating,vRating Rank,Highest Match Score,Highest Score Alliance, Most Recent Event Average
	8568B,Knights,North Andover High School,Massachusetts,United States,0,2293,62,1377,62,1622,45.50554203469,2243,112,6106B,78.66666666666667
	6916H,BVT Team H,Blackstone Valley Regional High School,Massachusetts,United States,0,2293,40,2695,40,2778,62.628527679903,1205,138,4478X81118P,97.05555555555556
	2442B,Bancroft Robodogs B,Bancroft School,Massachusetts,United States,12,1072,64,1332,64,1571,81.615867786521,427,119,2442C,79.21428571428571
	2625A,A,Worcester Technical High School,Massachusetts,United States,0,2293,10,4786,10,4816,-15.27827328969,6948,109,2442B2442C,48.1


Disclaimer
==========

The scripts included in this repository only collect data from vexDB and I have ABSOLUTELY NO IDEA what may go wrong. I do not take responsibility for outputs produced by the script, nor provide any warranty. 