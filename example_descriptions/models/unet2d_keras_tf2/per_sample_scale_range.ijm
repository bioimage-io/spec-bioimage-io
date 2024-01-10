// ----------------------------------------------------------------------------------------------
//Bioimage.IO pre-processing operation
//Further information at:
//https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#preprocessing
// ----------------------------------------------------------------------------------------------
// Operation: This macro calculates the 1th and 99.8th percentiles of an image histogram and clips the
//            intensity values between those two percentiles. The macro computes it for the entire
//            image regardless the number of channels or dimensions.
// kwargs
// - mode: per_sample (percentiles are computed for each sample individually), per_dataset (percentiles are computed for the entire dataset).
//	   For a fixed scaling use `scale linear`
// - axes the subset of axes to normalize jointly. For example xy to normalize the two image axes for 2d data jointly. The batch axis (b) is not valid here.
// - min_percentile the lower percentile used for normalization, in range 0 to 100.
// - max_percentile the upper percentile used for normalization, in range 1 to 100. Has to be bigger than upper_percentile.

// Credits of this macro:
// ----------------------------------------------------------------------------------------------
// - Base code from BenTupper http://imagej.1557.x6.nabble.com/Percentile-value-td3690983.html
// - DeepImageJ team:
// 		- Reference: "DeepImageJ: A user-friendly plugin to run deep learning models in ImageJ,
// 						E. Gomez-de-Mariscal, C. Garcia-Lopez-de-Haro, et al., bioRxiv 2019.
// ----------------------------------------------------------------------------------------------

// Edit these values as desired.
min_percentile = 1;
max_percentile = 99.8;
min_percentile = min_percentile/100;
max_percentile = max_percentile/100;
nBins = 256; // the larger the more accurate
// Check if the image is RGB
flag_rgb = !is("grayscale"); // "RGB = NOT (grayscale)"
// Convert the RGB image as a stack of slices so it processes the intensity of each slice.
if (flag_rgb==1){
	run("Make Composite");
	run("Stack to Images");
	run("Concatenate...", "  title=stack image1=[Red] image2=[Green] image3=[Blue]");
}

getDimensions(width, height, channels, slices, frames);
if (slices==1){
	axes = 'xy';
}
else {
	axes = 'xyz';
}
print("Percentile normalization to the axes: " + axes);
print("with min_percentile: " + min_percentile);
print("and max_percentile: " + max_percentile);

function percentile_normalization(min_percentile, max_percentile, nBins){

	//initialize the histogram
	cumHist = newArray(nBins);
	//move through each slice of the image to obtain the whole histogram
	getDimensions(width, height, channels, slices, frames);
	for (s = 1; s < slices+1; s++) {
		setSlice(s);
		getHistogram(values, counts, nBins);
		for (i = 0; i < nBins; i++) {
			cumHist[i] = cumHist[i] + counts[i];
		}
	}
	// cumulative histogram
	for (i = 1; i < nBins; i++) {
		cumHist[i] = cumHist[i] + cumHist[i-1];
		}
	//normalize the cumulative histogram
	normCumHist = newArray(nBins);
	for (i = 0; i < nBins; i++){  normCumHist[i] = cumHist[i]/cumHist[nBins - 1]; }

	// find the lower percentile (= min_percentile)
	target = min_percentile;
	i = 0;
	do {
        //print("i=" + i + "  value=" + values[i] + " cumHist= " + cumHist[i] + "  normCumHist= " + 100*normCumHist[i] );
        i = i + 1;

	} while (normCumHist[i] < target)
	mi = values[i];
	//print("Lower percentile has value " + mi);

	// find the upper percentile (= max_percentile)
	target = max_percentile;
	//i = 0;
	do {
        //print("i=" + i + "  value=" + values[i] + " cumHist= " + cumHist[i] + "  normCumHist= " + 100*normCumHist[i] );
        i = i + 1;
	} while (normCumHist[i] < target)
	ma = values[i];
	//print("Upper percentile has value " + ma);
	//normalization
	diff = ma-mi+1e-20; // add epsilon to avoid 0-divisions
	run("32-bit");
	run("Subtract...", "value="+mi+" stack");
	run("Divide...", "value="+diff+" stack");

}

// EXECUTE THE FUNCTION TO THE WHOLE IMAGE
percentile_normalization(min_percentile, max_percentile, nBins);
// Convert the slices into channel to avoid confussion between 3D and multichannel images.
if (flag_rgb==1){
	run("Properties...", "channels=3 slices=1 frames=1 pixel_width=1.0000 pixel_height=1.0000 voxel_depth=1.0000");
}
