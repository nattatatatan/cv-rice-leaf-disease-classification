University of Wollongong
School of Computing and information Technology

CSCI435/CSCI935 Computer Vision

Spring 2025

Group Projects (25 marks)
Due 11:30pm Sunday, 26 October 2025.

Introduction

In the group project, you will act as a computer vision practitioner and are required to work on the
following case: develop a solution, a reference implementation, and a comprehensive experimental
evaluation of the solution on the provided dataset, as well as generate a consulting report.

Case: Rice Leaf Disease Classification and Detection for Bangladeshi Local Rice

You are given a dataset  representing almost all the harmful diseases of rice in Bangladesh. This
dataset  consists  of  1106  images  of  five  harmful  diseases  called  Brown  Spot,  Leaf  Scald,  Rice
Blast,  Rice  Tungro,  and  Sheath  Blight,  in  two  different  background  variations  named  field
background  and white background.  The data is  collected from the rice  fields  of Dhaka  Division
and can be used for rice leaf disease classification and disease detection using Computer Vision
and Pattern Recognition. Following are some samples.

Image in Field

Image on a White Background

Disease

Rice Blast

Rice Tungro

Sheath Blight

Brown spot

Leaf scald

The dataset and its detailed description are available at here.

You are approached by a client for a computer vision method that can identify the disease present
in an image of a field or in an image with a white background. In other words, given a field image
or an image with a white background, the method needs to be able to predict the types of diseases,
assuming that the rice in the image has one of the five diseases. The provided dataset will be used
for developing and evaluating the system.

Requirements

You are required to

•  study  the  problem  by  inspecting  and  analysing  the  sample  images  that  are  available  for

download in Moodle.

•  search  for  relevant  literature  (papers)  from  the  IEEE  Xplore  database  that  is  available

through UoW’s library.

•

recommend or devise a method (algorithm),

•  provide an analysis of the pros and cons of the recommended method.

•  provide a reference implementation of the method

•  evaluate the method on the provided dataset and discuss the results, and

•  complete a consultation report for the client.

The  report  must  have  the  following  sections  and  will  be  marked  according  to  the  specified
requirements and its logical presentation. Use block diagrams or flowcharts whenever appropriate.

1. Coversheet

The coversheet should contain the following information: the title of the project, the names
of the group members, and the contributions of the individual members.

2. Executive Summary (1 mark) (up to 1/2 pages)

The  executive  summary  is  an  abstract  of  your  report  and  is  a  mini-report  that  precisely
summarises sections 3 to 6.

3. Problem Description (5 marks) (up to 1 page)

In  this  section,  you  should  describe  the  problem  and  translate  it  into  a  computer  vision
problem  after  studying  the  sample  images  and  the  client’s  requirements.  (JUST)  For
example, you may describe the computer vision problem as either an image classification
problem, an image segmentation problem, a shape detection problem, object detection, etc.,
or  a  combination  of  them  based  on  the  topics  that  have  been  covered  in  the  subject.
Diagrams, if any, should be numbered, captioned and referenced in the text properly.

Based on your description of the problem, an in-depth analysis of the characteristics of the
images and the challenges of the problem should be articulated. This analysis must support
the choice or design of the method to described in Section 5

4. Related Work (2 marks) (up to 2 page)

You need to search the IEEE Xplore database through UoW’s library and identify at least
4 papers published after 2021. These papers must be relevant to the problem. Read the
papers and provide a summary of these papers in this section in the context of the problem
described  in  Section  3.  You  need  to  organise  the  summary  logically  and  cite  the  papers
properly. The papers you are to summarise in this section must be listed in the reference
section  and  cited  using  IEEE  style  (i.e.,  to  cite  reference  one,  use  [1]).    Use  your  own
words;  direct  copying  from  the  papers  will  be  considered  plagiarism.  Diagrams,  if  any,
should be numbered and referenced in the text properly.

5. Method and Implementation (8 marks) (up to 3 pages)

In this section, you need to recommend a method or algorithm as a solution to the problem.
You  may  choose  an  algorithm  from  the  papers  you  just  studied  or  devise  your  own
algorithm.  In  either  case,  you  have  to  justify  why  you  recommend  such  an  algorithm  by
presenting the rationale behind your recommendation AND describing your algorithm step
by step in detail. Your description should be detailed enough so that someone (e.g., your
classmates)  with  some  background  knowledge  of  computer  vision  will  be  able  to
implement the algorithm. Organise the description logically, use your own words, and do
not  copy  anything  directly  from  any  books  or  papers!  Block  diagrams  or  algorithms  in
pseudocode are preferred, and they should be numbered and referenced in the text properly.

Also  in  this  section,  a  detailed  description  of  how  you  implement  the  recommended
algorithm should be provided. Note that this description of the implementation is different
from  the  actual  code.  The  description  may  include  modules  in  pseudocode.  Do  not  copy
python code directly; if you do, a heavy penalty will apply!

6. Experimental Results and Analysis (8 marks) (up to 2 pages)

In  this  section,  you  are  to  report  the  evaluation  of  the  recommended  method  on  the
provided dataset. The report should include the following subsections:

6.1 Experimental Settings

This  should  include  the  values  of  all  hyperparameters  you  used  to  generate  models,  the
results, a scheme to separate the training, validation (if any), and testing datasets; and a list
of experiments you have conducted.

6.2 Results

Results  of  each  experiment  listed  in  Section  6.1  are  reported  in  this  section.  All  results
should  be  an  average  over  5  runs  with  different  random  splits  (same  percentages)  of
training,  validation  (if  applicable),  and  testing.    Both  the  average  of  the  chosen
performance metrics and their standard deviation should be reported.

You need to report results for at least three scenarios:

a)  the test images have a white background
b)  the test images have a field background
c)  the test images are either with a white background or a field background

Note that it is acceptable that individual models to be used for these scenarios, and you are
free to use the provided dataset in any way as long as the test samples are not included in
the training of the models, and it is clearly stated in the report.

6.3 Discussion of the Results

This  section  provides  an  analysis  and  discussion  of  the  results,  particularly  concerning
whether the results meet your expectations of the recommended method; what the typically
successful  cases  are,  what  the  typically  failure  cases  are,  and  what  are  the  challenging
cases are, and explain the reasons for each.

Also, including in this section should be a discussion on how the method (not the dataset
size) may be improved.

7. References (1 mark)

All  references  should  be  listed  in  this  section.  IEEE  style  should  be  used.  Here  are  the
examples for fictitious conference papers and journal papers respectively.

[1]  D.  G.  Bailey,  “A  new  approach  to  lens  distortion  correction,"  in  Proceedings  of
International  Conference  on  Computer  Vision  and  Pattern  Recognition  (CVPR)
2025, pp.59-64.

[2]  G.  Wyvill,  C.  McPheeters,  and  B.  Wyvill,  “Data  structures  for  soft  objects,"  IEEE
Transactions  on  Pattern  Analysis  and  Machine  Intelligence  (PAMI),  vol.98,  pp.
227-234, 2025.

8.  Appendix: User Manual (up to 2 pages)

You must provide clear instructions on

a)  The packages required to run your code and how to install them, and
b)  how to run your code to reproduce the results included in your report.

Failing to provide such instructions will result in the reported results being considered not
reproducible and, hence, will incur a heavy penalty.

Format and maximum number of pages of the report:

To  ensure  that  your  PDF  report  is  readable  both  online  and  in  print,  you  must  follow  the
formatting requirements below:

•  Use a single-column layout with page numbers starting from 1 (excluding the cover page).
•  Use 12-point font.
•  Maintain a minimum margin of 1.25 cm on all sides.

The maximum number of pages for each section is listed above. Only content within the specified
page limits will be marked; anything beyond those limits will be ignored.

Requirements for the implementation:

(a)  The  program  MUST  be  in  Python.  The  permitted  packages  are  Python  3.12,  its  standard
libraries,  NumPy,  matplotlib,  OpenCV  4.12,  scikit-learn,  scikit-image,  and  pyTorch.  Other
packages that are specifically required by your method may also be permitted, but they must
be available and clear instructions to download and install them must be included in the user
manual. Failing to do so will be considered that the code does not run, and the results are
not reproducible.

(b) Your code must support the structure of the dataset folder. The path to the main dataset
is assumed to be “.\Dhan-Shomadhan\”. If you need to create interim data in different
folders, they must be under the main dataset folder and you must provide a tool in Python to
generate these folders and their content.

(c)  Use of pre-trained models is permittable. You must justify the use in the “Problem Description”
and  “Method  and  Implementation”  sections.  These  models  must  be  available  to  download.
Clear  instructions  should  be  given  on  how  to  download  and  where  to  place  them  in  the
Appendix: User Manual. Failing to do so will be considered that the code does not run, and
the results are not reproducible.

Submission
Zip  the  group_name.py  and  group_name.pdf  files  to  group_name.zip.  The  zip  file
must be submitted via Moodle.

IMPORTANT:

•  DO NOT include and submit the image folders and any interim data in the zip file. Your

submission may not be accepted if you do so.
•  Submission through email WILL NOT be accepted.


