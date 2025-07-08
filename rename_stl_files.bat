@echo off
echo 批量重命名SolidWorks转换的STL文件

rem 假设转换后的文件名为原始名称
if exist "RD20-FR3-V6.0-1.stl" ren "RD20-FR3-V6.0-1.stl" "fr3_base.stl"
if exist "RD20-FR3-V6.0-2.stl" ren "RD20-FR3-V6.0-2.stl" "fr3_link1.stl"  
if exist "RD20-FR3-V6.0-3.stl" ren "RD20-FR3-V6.0-3.stl" "fr3_link2.stl"
if exist "RD20-FR3-V6.0-4.stl" ren "RD20-FR3-V6.0-4.stl" "fr3_link3.stl"
if exist "RD20-FR3-V6.0-5.stl" ren "RD20-FR3-V6.0-5.stl" "fr3_link4.stl"
if exist "RD20-FR3-V6.0-7.stl" ren "RD20-FR3-V6.0-7.stl" "fr3_gripper.stl"

echo 重命名完成
pause
