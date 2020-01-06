# Analyzing air quality in Stuttgart using official and Citizen-Science data

besserer Titel? Routing?


## 1. Introduction

Irgend ein besserer Einleitungssatz als:

Over the last few years, the city of Stuttgart has been in the focus of media and scientific interest due to increased
levels of particulate matter.

&nbsp;

Atmospheric particulate matter (PM) is solid or liquid matter suspended in the atmosphere with diameters of under
10 µm (coare-particle matter) or under 2.5 µm (fine-particle matter) (Fuzzi et al 2015 pp. 8228).
In the past years, there has been a high interest in particulate matter and its effects on human health
(Fuzzi et al 2015 p. 8217).

Short-term exposure to particulate matter can cause in?ammation of the respiratory system,
immune response and oxidative stress to the affected cells (Ristovski, Z. et al. 2005, p. 205). 

Long term exposure to elevated levels of particulate matter can lead to increased mortiality due to 
nonallergic respiratory morbidity, allergic illness and symptoms (such as asthma), cardiovascular morbidity, cancer,
and effects pregnancy, birth outcomes and male fertility (Heinrich et al 2005, pp. 132).

It is also the area of interest of an ongoing project by the German Federal Ministry of Transport and Digital
Infrastructure (BMVI): The Satellite-based system for displaying, predicting and simulating air pollutants for
sustainable urban and regional development ("Satellitenbasiertes System zur Anzeige, Prognose und Simulation
von Luftschadstoffen für eine nachhaltige Stadt- und Regionalentwicklung - SAUBER").

At the same time, while cycling has no direct adverse effect on the air quality - cyclists themselves are directly
subjected to air pollution within a city, as cycle paths are usually in immediate proximity to roads.
Analyzing and mapping this concentration and distribution of particulate matter - and to map a 'least-polluted' route
through particularly affected areas - is a step towards informing about - and protecting users from - air pollution
in the city of Stuttgart. 

It is also a step towards informing decision-making processes e.g. for guiding the traffic of combustion engine vehicles
and possibly enforce restrictions on it in order to reduce air pollution.

It is vital for the analysis to combine official datasets with more extensive open source data, as a recent study on the
impact of driving bans in Stuttgart states that "The sparsity \[of the sensor network\] introduces uncertainty which
cannot be modeled correctly or can not be modeled at all"(Wolfmann et al 2019, pp. 295)

The goal of this analysis is thus  to provide a small-scale geographic analysis of the particulate matter concentration
in the city of Stuttgart; making the resulting map available on a user-interface; and allowing users to combine
the results with a routing service informed by the result of the analysis.

&nbsp;

## 2. Literature research
Li et al. (2014) used inverse-distance kriging for interpolating particulate matter from point locations. 

tbc

&nbsp;


## 3. Data 
### 3.1 Particulate matter

Air quality measurements in Stuttgart and the State of Baden-Württemberg is conducted by the State Office for
the Environment, Measurements and Nature Conservation of the Federal State of Baden-Württemberg (LUBW).
The LUBW operates 44 measuring stations within the State of Baden-Württemberg, with 5 stations
located within Stuttgart itself.
Upon request, direct access to the measuring station data was not provided by the LUBW.
Thus, the first goal of the project will be to access and automatically download the output of the LUBW's publically
available data at https://www.lubw.baden-wuerttemberg.de/luft/messwerte-immissionswerte.
The site provides an hourly average of Ozone (O3) and Nitrogen dioxide (NO2);
and a moving 24-hour average of particulate matter (PM2.5, PM10).
To supplement these measurements, the Stuttgart-based project Luftdaten.info was brought into life.
As a 'Citizen Science'-project, it offers shopping and building instructions for inexpensive particulate matter 
sensors (mainly the Nova Fitness Co., Ltd. SDS011), and multiple APIs at
https://github.com/opendata-stuttgart/meta/wiki/APIs to access the recorded data, which are queryable for
e.g. geographic bounding boxes, and with a temporal resolution of down to 5 minutes.

The strength of the project is the relatively very high density of sensors - especially within the city of Stuttgart.
A simple bounding-box query of all active sensor around in the greater area of Stuttgart has yielded 1350 sensors. 
Apart from the non-standarized installation of the sensor, the accuracy of measurements of the SDS011 sensor
was investigated by the LUBW (2017) and discussed in Blon (2017). 

Direct comparisons of the accuracy of the PM-meauring devices used in the Luftdaten.info project has shown that while
the SDS011 perform measurements comparable to the calibrated, high-accuracy sensors used by the LUBW in conditions
of 50-70% air humidity and below 20�g/m3 PM concentration.
Above these thresholds, or under chaning atmospheric conditions respectively, the reported concentrations
by the SDS011 show significant discrepancies (LUBW 2017, p.5).


Since the smallest temporal resolution offered by the LUBW is one hour, and the accuracy of the SDS011 data seems
to benefit from using aggregate data, the project's aim is to use hourly data from the Luftdaten.info project.
Additionally, subsequent analyses based on this project can utilize different queries on Luftdaten.info APIs in terms
of geographical area, temporal resolution, etc. with little effort. 

The hourly data can be categorized by using the _Common Air Quality Index_ (CAQI) which was standardized for yearly,
daily and hourly measures ([3])

### 3.2 Road network 

Automatic download from OpenStreetMap

## 4. Analysis 

### 4.1 Download and pre-processing
For the automated download of both the air quality and road network data, both Windows or Linux operating systems
provide adequate tools like wget or curl, whose behaviour can be controlled via simple scripting e.g. in bash.
For an automated, scheduled download, tools like cron or Windows Task Scheduler can be used to initiate
the finished script.
To store the expectedly numerous datasets, a database, including a fitting data-model will be implemented.
PostGIS, an extension to the Free and Open Source relational Database Management System PostgreSQL, offers support
of geographic data types and simple georgraphical analyses. 
Before ingesting the data, the raw downloaded files data then need to be parsed and pre-processed
for the subsequent analysis.
Both the Python and PostgreSQL's PL/pgSQL scripting language offer support for the xml data of the LUBW and
the JSON datatype of Luftdaten.info in order to automate the parsing and ingestion of the data.

### 4.2 Comparing official and crowd-sourced data
In order to assess the real-life comparability of official air quality measurements with Citizen Science data,
a simple comparison between stations of either origin and in close proximity of each other will be conducted using
simple statistical methods, which can be implemented directly in the database or via scripting languages such as Python.
 
### 4.3 Interpolation
Air quality and air pollution are spatio-temporal  ('4-D') data. Meanwhile, the measurements of air pollution by
official or distributed measuring stations are point-data.  
An analysis of the concentation of particulate matter within the city of Stuttgart needs to interpolate the measured
concentration of particulate matter at one station with its surrounding environment.
Within its scope, this analysis aims for a two dimensional modelling of the atmospheric concentration of PM via Free
and Open Source GIS. 
PostGIS offers a limited range of interpolation methods, such as simple Buffering[1] and Inverted-Distance Weighting[2].
While performing in-database calculations offer benefits in speed and transactional integrity, these methods can be
expanded using additional FOSSGIS-software such as GRASS GIS.
GRASS offers an interface to import and export data to and from PostGIS databases, and additional interpolation
methods such as Kriging, different methods of Splinging (B-Splines, Regularized Spline with Tension) and
Inverse Cost Weighting; the latter of which can take into account cost surfaces, e.g. buildings within a city. 
A part of the analysis will be to compare different methods offered by both GISs of interpolating the measured
PM concentrations with the surrounding environment. 

### 4.4 Routing 
If possible

### 6. Sources 
Heinrich, J. et al. (2005): Studies on health effects of transport-related air pollution. In: Krzyzanowski, M. et al.:
Health effects of transport-related air pollution. WHO Regional Office Europe.

Li, L.; Losser, T.; Yorke, C.; Piltner, R. Fast Inverse Distance Weighting-Based Spatiotemporal Interpolation:
A Web-Based Application of Interpolating Daily Fine Particulate Matter PM2.5 in the Contiguous U.S. Using Parallel
Programming and k-d Tree. Int. J. Environ. Res. Public Health 2014, 11, 9101-9141.

Ristovski, Z. et al. (2012): Respiratory health effects of diesel particulate matter. In: Respirology (2012) 17, 201�212.

Li, L. et al. (2014): Fast Inverse Distance Weighting-Based Spatiotemporal Interpolation: A Web-Based Application of
Interpolating Daily Fine Particulate Matter PM2.5 in the Contiguous U.S. Using Parallel Programming and k-d Tree.
In: International Journal of Environmental Research and Public Health  2014, 11 (9), 9101-9141.

Woltmann, L. et al. (2019): Assessing the Impact of Driving Bans with Data Analysis. In: H. Meyer et al. (Hrsg.):
BTW 2019 — Workshopband, Lecture Notes in Informatics (LNI), Gesellschaft für Informatik, Bonn 2019  287.
Online: https://dl.gi.de/bitstream/handle/20.500.12116/21819/G2-1.pdf?sequence=1

[1]https://postgis.net/docs/ST_Buffer.html
[2]https://postgis.net/docs/RT_ST_InvDistWeight4ma.html
[3]http://www.airqualitynow.eu/about_indices_definition.php
