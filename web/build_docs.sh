#!/bin/bash
dir_design=docs-design
dir_testcases=docs-testcases

rm -rf $dir_design
# Build html documentation
echo Building design documentation...
cd ../docs/design_documentation && make html
echo Finished building design documentation.
# Move build to directory within /web
echo Moving design documentation to $dir_design...
cd ../../web && cp -r ../docs/design_documentation/build/html $dir_design
echo Finished moving design documentation.
# Flatten directory for images and remove sphinx source and static build
#echo Flattening design documentation images...
#cd $dir_design/_images
#for file in ./*.png; do
#	cp $file ../$file
#done
#cd $dir_design/_images/math
#for file in ./*.png; do
#	cp $file ../../$file
#done
#cd ../
cd $dir_design && mv _images images && mv _sources sources && mv _static static
echo Finished flattening design documentation images.
# Replace image file locations in html text
for file in ./*.html; do
	sed -i 's/"_images\//"images\//g' $file
	sed -i 's/"_sources\//"sources\//g' $file
	sed -i 's/"_static\//"static\//g' $file
	sed -i 's/"_static\//"static\//g' $file
done
# Add html documents as pages in jekyll
echo Add design documentation as jekyll title page...
for file in ./*html; do
	echo $file
	if [[ $file == "./index.html" ]]; then
		echo -e '---\ntitle: Design\n---' | cat - index.html > temp && mv temp index.html
		echo index.html made jekyll title.
	elif [[ $file == "./appendix_KPI.html" ]]; then
		echo WARNING: Not including appendix_KPI.html as jekyll page.
	fi
	# Make documentation navbar below jekyll navbar
	sed -i 's/ navbar-fixed-top//g' $file
done
echo Finished adding design documentation as jekyll title page.


# Move test case documentation to directory within /web
echo Moving test case documentation to $dir_testcases...
cd ..
rm -r $dir_testcases
mkdir $dir_testcases
cp -r ../testcases/bestest_air/doc $dir_testcases/bestest_air
cp -r ../testcases/bestest_hydronic/doc $dir_testcases/bestest_hydronic
cp -r ../testcases/bestest_hydronic_heat_pump/doc $dir_testcases/bestest_hydronic_heat_pump
cp -r ../testcases/multizone_residential_hydronic/doc $dir_testcases/multizone_residential_hydronic
cp -r ../testcases/singlezone_commercial_hydronic/doc $dir_testcases/singlezone_commercial_hydronic
echo Finished test case design documentation.
