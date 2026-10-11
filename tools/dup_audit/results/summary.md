# Near-duplicate audit with SIFT + RANSAC (one-off, read-only)

## Method

- Features: RootSIFT, cached cache/ images resized to long side 800 px, cap 1500 keypoints, contrastThreshold 0.005 (white-background leaves are texture-poor; default 0.04 gave a median of 25 keypoints). Stored in feats2.pkl.
- White domain: keypoints restricted to a leaf mask (HSV saturation Otsu, closed, holes filled so pale lesions stay in, dilated 10 px). A first unmasked pass produced hundreds of false pairs: matches on the wall (sensor noise, smudges at the same position) gave identity-like homographies, and degenerate homographies collapsed one image to a point. That pass was discarded.
- Matching: brute-force kNN, Lowe ratio 0.75. Geometry: homography RANSAC (6 px) and fundamental matrix RANSAC (1.5 px). Fits are rejected when degenerate: homography singular values outside 0.33-3, perspective terms above 2e-3, or the inlier cloud spanning less than 40 px (principal axis, 5-95 pct) in either image. A mask-value bug in the first F count (255-valued masks) was fixed.
- Score used for ranking: field-field pairs = max(H inliers, F inliers) because canopy scenes are not planar (e.g. rbf_13/rbf_14: H=129, F=196). Any pair involving a white image = H inliers only, because F fitted on a few matches over a narrow leaf is under-constrained (F-only fits gave many 'inliers = all matches' artefacts in the null).
- Coverage: white same-class 64553/64553; field same-class 11444/11444; field-white same-class 52704/52704; field cross-class 45172/45172; white cross-class 172127/230743 (75%, stopped on coordinator request). Not run: field-white cross-class, white-field cross-class.
- Runtime: feature extraction about 2 min. Pair matching about 1h50 wall in total, of which about 50 min was a discarded first pass; the machine was shared (load average 100+), the pool was paused once, and the second pass ran on 3 workers at the end. Uncontended cost is roughly 6 ms/pair for white and 40 ms/pair for field-field on one core.

## Calibration

Synthetic bursts (40 random images per domain per set, original vs transformed copy; transformed copy goes through the same pipeline including the leaf mask):

| domain | set | transform | min | p5 | p25 | median |
|---|---|---|---|---|---|---|
| white | spec | crop 70-95% area, rot +-5, scale 0.8-1.2, brightness +-10%, JPEG 70-95 | 19 | 21.8 | 65.5 | 123 |
| white | hard | crop 35-60%, rot +-10, scale 0.6-1.4 | 11 | 15.8 | 43.8 | 81 |
| field | spec | as spec | 578 | 670 | 790 | 840 |
| field | hard | as hard | 213 | 294 | 407 | 501 |

Null (unrelated pairs = cross-class pairs, assumed different leaves/scenes):

- field cross-class (45172 pairs): max 16, none >= 20 (all >= 15 are F-only with n_good=16, H=0).
- white cross-class (172127 pairs): max 36; 5 pairs >= 19. All viewed are different leaves; the matches lie along the leaf axis (vein texture is nearly 1-D periodic, so a homography is under-constrained and RANSAC finds a consistent translation).
- field-white same-class (52704 pairs): max 9.

Thresholds:

- Field: score >= 20. Null max 16, hard-burst min 213, real pairs in the data jump from 16 to 20+. There is a wide empty gap, so the exact value does not matter between 17 and about 40.
- White: inliers alone do not separate well. Null max is 36 (vein texture), spec bursts have p5 = 21.8 and min 19. Using >= 40 is clean against the null (5 same-class pairs) but misses weaker true bursts. Practical rule: score >= 20 AND consecutive file number (gap <= 3), or score >= 40. Evidence that this is sound: all 14 white same-class pairs with score >= 15 have consecutive file numbers (764 consecutive pairs exist, none of the 63789 non-consecutive pairs reaches 10); the null has no such structure.

## Key finding

Duplicates are bursts of consecutively numbered files (the dataset was photographed in series). The earlier dHash audit found none in field because reframed shots defeat dHash. Field: 32 same-class pairs >= 20, up to 799 inliers; 22 are gap 1, 27 are gap <= 3, the rest (gap 5, 11, 11, 18, 46) include genuine same-scene pairs (lsf_67/lsf_72, lsf_12/lsf_23, lsf_34/lsf_45) and two F-only doubtful ones (sbf_1 vs sbf_19, sbf_47). Recommend building connected components over pairs with score >= 20 (field) and the white rule above, and splitting by component.

## Inlier histogram (score) per group

| group | pairs | 0 | 1-7 | 8-9 | 10-11 | 12-14 | 15-19 | 20-24 | 25-29 | 30-39 | 40-59 | 60-99 | 100-199 | 200+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| field same-class | 11444 / 11444 | 10197 | 63 | 842 | 254 | 47 | 9 | 3 | 1 | 1 | 2 | 6 | 8 | 11 |
| field cross-class | 45172 / 45172 | 42561 | 286 | 1939 | 343 | 36 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| field-white same-class | 52704 / 52704 | 52694 | 9 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| white same-class | 64553 / 64553 | 64513 | 16 | 5 | 1 | 4 | 1 | 5 | 2 | 1 | 3 | 1 | 1 | 0 |
| white cross-class | 172127 / 230743 | 172092 | 26 | 0 | 2 | 2 | 1 | 2 | 0 | 2 | 0 | 0 | 0 | 0 |

Spikes at 8 to 9 and 16 are F-fit artefacts at n_good = 8 and 16, not structure.

## Verdicts: field same-class top 32 (sheets sift_top_field_01..05.png; 01-04 are ranks 1-24, 05 is ranks 25-32)

| rank | file_a | file_b | H | F | score | verdict |
|---|---|---|---|---|---|---|
| 1 | rtf_32.jpg | rtf_33.jpg | 788 | 799 | 799 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 2 | rtf_10.jpg | rtf_9.jpg | 724 | 696 | 724 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 3 | rbf_21.jpg | rbf_22.jpg | 607 | 557 | 607 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 4 | rtf_22.jpg | rtf_23.jpg | 521 | 495 | 521 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 5 | rtf_0.jpg | rtf_1.jpg | 456 | 464 | 464 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 6 | rtf_17.jpg | rtf_18.jpg | 457 | 421 | 457 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 7 | rtf_5.jpg | rtf_6.jpg | 371 | 364 | 371 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 8 | lsf_67.jpg | lsf_72.jpg | 318 | 307 | 318 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 9 | bsf_7.jpg | bsf_8.jpg | 253 | 251 | 253 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 10 | rtf_7.jpg | rtf_9.jpg | 240 | 229 | 240 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 11 | rtf_10.jpg | rtf_7.jpg | 227 | 217 | 227 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 12 | rtf_26.jpg | rtf_27.jpg | 198 | 174 | 198 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 13 | rtf_8.jpg | rtf_9.jpg | 196 | 179 | 196 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 14 | rbf_13.jpg | rbf_14.jpg | 129 | 196 | 196 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 15 | rtf_7.jpg | rtf_8.jpg | 192 | 172 | 192 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 16 | lsf_6.jpg | lsf_7.jpg | 111 | 160 | 160 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 17 | rtf_10.jpg | rtf_8.jpg | 155 | 131 | 155 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 18 | rtf_20.jpg | rtf_21.jpg | 132 | 111 | 132 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 19 | bsf_4.jpg | bsf_5.jpg | 94 | 101 | 101 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 20 | lsf_0.jpg | lsf_1.jpg | 85 | 83 | 85 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 21 | rtf_18.jpg | rtf_19.jpg | 79 | 72 | 79 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 22 | bsf_2.jpg | bsf_3.jpg | 74 | 73 | 74 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 23 | bsf_0.jpg | bsf_1.jpg | 59 | 67 | 67 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 24 | rtf_17.jpg | rtf_19.jpg | 67 | 63 | 67 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 25 | rtf_11.jpg | rtf_12.jpg | 60 | 56 | 60 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 26 | rbf_1.jpg | rbf_2.jpg | 36 | 49 | 49 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 27 | lsf_12.jpg | lsf_23.jpg | 42 | 44 | 44 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 28 | lsf_34.jpg | lsf_45.jpg | 36 | 32 | 36 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 29 | bsf_15.jpg | bsf_16.jpg | 24 | 25 | 25 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 30 | rtf_25.jpg | rtf_27.jpg | 19 | 24 | 24 | likely duplicate - same scene, same plants, reframed/shifted shot (viewed) |
| 31 | sbf_1.jpg | sbf_19.jpg | 0 | 23 | 23 | unsure, leaning different - F-only (H=0), matches converge on one point, scene not clearly the same (viewed) |
| 32 | sbf_1.jpg | sbf_47.jpg | 0 | 20 | 20 | unsure, leaning different - F-only (H=0), matches converge on one point, scene not clearly the same (viewed) |

## Verdicts: white same-class top 24 (sheets sift_top_white_01..04.png)

| rank | file_a | file_b | H | F | score | verdict |
|---|---|---|---|---|---|---|
| 1 | rb_wb_169.jpg | rb_wb_170.jpg | 110 | 107 | 110 | likely duplicate - same specimen (consecutive files, 90+ H inliers, matching lesion pattern/leaf shape); viewed |
| 2 | ls_wb_1.jpg | ls_wb_2.jpg | 93 | 79 | 93 | likely duplicate - same specimen (consecutive files, 90+ H inliers, matching lesion pattern/leaf shape); viewed |
| 3 | rb_wb_146.jpg | rb_wb_147.jpg | 53 | 53 | 53 | unsure, leaning same specimen - consecutive file numbers, score above the usual null for the top 5 only; matches are along the leaf axis so vein-texture ambiguity cannot be ruled out (viewed) |
| 4 | sb_wb_210.jpg | sb_wb_211.jpg | 46 | 48 | 46 | unsure, leaning same specimen - consecutive file numbers, score above the usual null for the top 5 only; matches are along the leaf axis so vein-texture ambiguity cannot be ruled out (viewed) |
| 5 | bs_wb_4.jpg | bs_wb_5.jpg | 43 | 44 | 43 | unsure, leaning same specimen - consecutive file numbers, score above the usual null for the top 5 only; matches are along the leaf axis so vein-texture ambiguity cannot be ruled out (viewed) |
| 6 | bs_wb_55.jpg | bs_wb_56.jpg | 32 | 32 | 32 | unsure - score within the white null range (<= 36) but consecutive file number; leaf looks like the same specimen but at a different position/crop (viewed) |
| 7 | ls_wb_85.jpg | ls_wb_86.jpg | 29 | 28 | 29 | unsure - score within the white null range (<= 36) but consecutive file number; leaf looks like the same specimen but at a different position/crop (viewed) |
| 8 | rb_wb_180.jpg | rb_wb_181.jpg | 27 | 27 | 27 | unsure - score within the white null range (<= 36) but consecutive file number; leaf looks like the same specimen but at a different position/crop (viewed) |
| 9 | rb_wb_91.jpg | rb_wb_92.jpg | 23 | 25 | 23 | unsure - score within the white null range (<= 36) but consecutive file number; leaf looks like the same specimen but at a different position/crop (viewed) |
| 10 | rb_wb_20.jpg | rb_wb_21.jpg | 22 | 24 | 22 | unsure - score within the white null range (<= 36) but consecutive file number; leaf looks like the same specimen but at a different position/crop (viewed) |
| 11 | rb_wb_113.jpg | rb_wb_114.jpg | 21 | 19 | 21 | unsure - score within the white null range (<= 36) but consecutive file number; leaf looks like the same specimen but at a different position/crop (viewed) |
| 12 | bs_wb_80.jpg | bs_wb_81.jpg | 20 | 22 | 20 | unsure - score within the white null range (<= 36) but consecutive file number; leaf looks like the same specimen but at a different position/crop (viewed) |
| 13 | ls_wb_100.jpg | ls_wb_99.jpg | 20 | 21 | 20 | unsure - score within the white null range (<= 36) but consecutive file number; leaf looks like the same specimen but at a different position/crop (viewed) |
| 14 | rb_wb_136.jpg | rb_wb_137.jpg | 15 | 17 | 15 | unsure - weak (13-20 inliers), consecutive files, geometry loose (viewed) |
| 15 | bs_wb_10.jpg | bs_wb_11.jpg | 13 | 15 | 13 | unsure - weak (13-20 inliers), consecutive files, geometry loose (viewed) |
| 16 | sb_wb_200.jpg | sb_wb_201.jpg | 13 | 19 | 13 | unsure - weak (13-20 inliers), consecutive files, geometry loose (viewed) |
| 17 | rt_wb_104.jpg | rt_wb_105.jpg | 13 | 15 | 13 | unsure - weak (13-20 inliers), consecutive files, geometry loose (viewed) |
| 18 | rb_wb_171.jpg | rb_wb_172.jpg | 13 | 16 | 13 | unsure - weak (13-20 inliers), consecutive files, geometry loose (viewed) |
| 19 | rb_wb_26.jpg | rb_wb_27.jpg | 11 | 13 | 11 | likely different - score <= 11, below any threshold (sheet 04 not inspected) |
| 20 | bs_wb_67.jpg | bs_wb_68.jpg | 9 | 0 | 9 | likely different - score <= 11, below any threshold (sheet 04 not inspected) |
| 21 | ls_wb_119.jpg | ls_wb_33.jpg | 8 | 12 | 8 | likely different - score <= 11, below any threshold (sheet 04 not inspected) |
| 22 | sb_wb_154.jpg | sb_wb_79.jpg | 8 | 0 | 8 | likely different - score <= 11, below any threshold (sheet 04 not inspected) |
| 23 | rb_wb_177.jpg | rb_wb_178.jpg | 8 | 0 | 8 | likely different - score <= 11, below any threshold (sheet 04 not inspected) |
| 24 | rb_wb_14.jpg | rb_wb_15.jpg | 8 | 0 | 8 | likely different - score <= 11, below any threshold (sheet 04 not inspected) |

## Verdicts: top 8 cross-class (field + white; sheet sift_top_crossclass_01.png)

| rank | file_a | file_b | H | F | score | verdict |
|---|---|---|---|---|---|---|
| 1 | bs_wb_66.jpg | ls_wb_104.jpg | 36 | 35 | 36 | likely different - different leaves (colour/lesions differ), matches are axis-aligned vein texture (viewed) |
| 2 | ls_wb_98.jpg | rb_wb_125.jpg | 30 | 32 | 30 | likely different - different leaves (colour/lesions differ), matches are axis-aligned vein texture (viewed) |
| 3 | ls_wb_128.jpg | rb_wb_189.jpg | 23 | 24 | 23 | likely different - different leaves (colour/lesions differ), matches are axis-aligned vein texture (viewed) |
| 4 | bs_wb_58.jpg | ls_wb_79.jpg | 20 | 22 | 20 | likely different - different leaves (colour/lesions differ), matches are axis-aligned vein texture (viewed) |
| 5 | ls_wb_123.jpg | rb_wb_184.jpg | 19 | 20 | 19 | likely different - different leaves (colour/lesions differ), matches are axis-aligned vein texture (viewed) |
| 6 | lsf_31.jpg | rtf_24.jpg | 0 | 16 | 16 | likely different - F-only, 16 matches, different scenes (viewed) |
| 7 | bsf_29.jpg | lsf_15.jpg | 0 | 16 | 16 | likely different - F-only, 16 matches, different scenes (viewed) |
| 8 | bsf_26.jpg | lsf_72.jpg | 0 | 16 | 16 | likely different - F-only, 16 matches, different scenes (viewed) |

No field cross-class pair exceeds 16, so there is no sign of one scene labelled with two diseases in the field domain. White cross-class is only 75% covered; its top pairs are spurious.

## Top 8 field-white same-class (sheet sift_top_fieldwhite_01.png)

| rank | file_a | file_b | H | F | score | verdict |
|---|---|---|---|---|---|---|
| 1 | sb_wb_164.jpg | sbf_35.jpg | 9 | 9 | 9 | likely different - max score 9, below any threshold (sheet sift_top_fieldwhite_01.png not inspected) |
| 2 | sb_wb_151.jpg | sbf_62.jpg | 5 | 0 | 5 | likely different - max score 9, below any threshold (sheet sift_top_fieldwhite_01.png not inspected) |
| 3 | rb_wb_146.jpg | rbf_42.jpg | 5 | 0 | 5 | likely different - max score 9, below any threshold (sheet sift_top_fieldwhite_01.png not inspected) |
| 4 | ls_wb_81.jpg | lsf_32.jpg | 5 | 0 | 5 | likely different - max score 9, below any threshold (sheet sift_top_fieldwhite_01.png not inspected) |
| 5 | rb_wb_142.jpg | rbf_1.jpg | 5 | 0 | 5 | likely different - max score 9, below any threshold (sheet sift_top_fieldwhite_01.png not inspected) |
| 6 | sb_wb_170.jpg | sbf_35.jpg | 4 | 0 | 4 | likely different - max score 9, below any threshold (sheet sift_top_fieldwhite_01.png not inspected) |
| 7 | rb_wb_126.jpg | rbf_5.jpg | 4 | 0 | 4 | likely different - max score 9, below any threshold (sheet sift_top_fieldwhite_01.png not inspected) |
| 8 | sb_wb_162.jpg | sbf_50.jpg | 4 | 0 | 4 | likely different - max score 9, below any threshold (sheet sift_top_fieldwhite_01.png not inspected) |

## Files

- pairs_sift.csv: all pairs with score >= 15 (67 rows). Columns: file_a, file_b, class_a, class_b, domain_a, domain_b, inliers (= the score defined above), match_ratio (score / min keypoints), inliers_H, inliers_F, n_good, group.
- sift_top_field_01..05.png, sift_top_white_01..04.png, sift_top_crossclass_01.png, sift_top_fieldwhite_01.png.
- calib_bursts2.csv (header is slightly off: columns domain, set, file, kp_a, kp_b, n_good, H, F, Hraw), final_pairs.pkl (all evaluated pairs), scripts in this directory.