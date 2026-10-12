# Methods: plain unified model vs Method A (composites) vs Method B (segment, crop)

Mean +- std over the 5 splits (std with ddof=1). Plain is the unified model of the G1 backbone; A adds composites to its training data; B crops every image to the box of its split's leaf segmenter. Gate G2 uses only the val rows. The paired rows are the per-split difference minus plain. Test rows are shown only after gate G2 froze the recommendation. Rows that are not complete yet read 'pending'.

| Part | Method | Experiment | White macro-F1 | White accuracy (%) | Field macro-F1 | Field accuracy (%) | Mixed macro-F1 | Mixed accuracy (%) | Domain-balanced macro-F1 | Domain-balanced accuracy (%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| val | plain unified model | (G1 backbone not chosen) | pending | pending | pending | pending | pending | pending | pending | pending |
| val | Method A (composites) | E3-A | pending | pending | pending | pending | pending | pending | pending | pending |
| val | Method B (segment, crop) | E4-B | pending | pending | pending | pending | pending | pending | pending | pending |
| val | A - plain (paired) | E3-A - plain | pending | pending | pending | pending | pending | pending | pending | pending |
| val | B - plain (paired) | E4-B - plain | pending | pending | pending | pending | pending | pending | pending | pending |
| test | plain unified model | (G1 backbone not chosen) | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 |
| test | Method A (composites) | E3-A | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 |
| test | Method B (segment, crop) | E4-B | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 |
| test | A - plain (paired) | E3-A - plain | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 |
| test | B - plain (paired) | E4-B - plain | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 | hidden until gate g2 |
