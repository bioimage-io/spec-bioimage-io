
// ----------------------------------------------------------------------------------------------
// This macro converts an image with float values between 0 and 1 and three channels
// (background/froreground/cell contours)into an instance segmentation image, in which
// each cell has a unique label. The segmentation is postprocessed using MorpholibJ
// watershed postprocessing. To distinguish the cells from the background, it segments
// the foregroung channel with values >= 0.5.
// Credits:
// - DeepImageJ team:
// 		- Reference: DeepImageJ: A user-friendly environment to run deep learning models in ImageJ,
// 			     E. Gómez-de-Mariscal, C. García-López-de-Haro, W. Ouyang, L. Donati, E. Lundberg, M. Unser, A. Muñoz-Barrutia, D. Sage,
//             	             Nat Methods 18, 1192–1195 (2021). https://doi.org/10.1038/s41592-021-01262-9
// ----------------------------------------------------------------------------------------------

// Rename output image
rename("output");

// Display in grayscale
Stack.setDisplayMode("grayscale");

// "argmax"
setThreshold(0.5, 1.0);
setOption("BlackBackground", true);
run("Convert to Mask", "method=Mean background=Dark black");
run("Divide...", "value=255.000 stack");
setSlice(1);
run("Multiply...", "value=0 slice");
setSlice(2);
run("Multiply...", "value=1 slice");
setSlice(3);
run("Multiply...", "value=2 slice");
run("Z Project...", "projection=[Max Intensity]");
rename("argmax");
close( "output" )

// Analyze foreground (1) label only
run("Select Label(s)", "label(s)=1");
close("argmax")
selectWindow("argmax-keepLabels");
// Fill holes
run("Fill Holes (Binary/Gray)");
close("argmax-keepLabels");
// Convert to 0-255
run("Multiply...", "value=255.000");
// Apply distance transform watershed to extract objects
run("Distance Transform Watershed", "distances=[Borgefors (3,4)] output=[32 bits] normalize dynamic=1 connectivity=4");
close("argmax-keepLabels-fillHoles");
// Remove small objects
run("Label Size Filtering", "operation=Greater_Than size=10");
close("argmax-keepLabels-fillHoles-dist-watershed");
// Rename final image and assign color map
selectWindow("argmax-keepLabels-fillHoles-dist-watershed-sizeFilt");
rename( "segmented-cells" );
run("Set Label Map", "colormap=[Golden angle] background=White shuffle");
resetMinAndMax();
