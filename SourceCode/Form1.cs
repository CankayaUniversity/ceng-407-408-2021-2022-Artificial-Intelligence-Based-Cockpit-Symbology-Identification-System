using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SeniorProject
{
    public partial class Form1 : Form
    {
        public string imageFilePath;
        public string filePath;
        private string PythonDirectory = @"..\..\PythonCode\";
        //private string PythonDirectory = @"PythonCode\";

        DataGridViewRow row;
        DataGridViewRow row3;
        DataGridViewRow row4;
        DataGridViewRow row5;

        public Form1()
        {
            InitializeComponent();
            row = (DataGridViewRow)dataGridView1.Rows[0].Clone();
            row.Cells[0].Value = "Airspeed";
            dataGridView1.Rows.Add(row);
            //DataGridViewRow row2 = (DataGridViewRow)dataGridView1.Rows[0].Clone();
            //row2.Cells[0].Value = "Attitude";
            //dataGridView1.Rows.Add(row2);
            row3 = (DataGridViewRow)dataGridView1.Rows[0].Clone();
            row3.Cells[0].Value = "Altimeter";
            dataGridView1.Rows.Add(row3);
            row4 = (DataGridViewRow)dataGridView1.Rows[0].Clone();
            row4.Cells[0].Value = "Vertical Speed";
            dataGridView1.Rows.Add(row4);
            row5 = (DataGridViewRow)dataGridView1.Rows[0].Clone();
            row5.Cells[0].Value = "Horizontal Situation";
            dataGridView1.Rows.Add(row5);

            groupBox2.Visible = false;
            groupBox3.Visible = false;
            groupBox4.Visible = false;
        }

        private void btn_SelectImage_Click(object sender, EventArgs e)
        {

            groupBox1.BackgroundImage = SeniorProject.Properties.Resources.SkyBackground;
            groupBox3.Visible = false;
            imageAirplane.Visible = false;

            using (OpenFileDialog openFileDialog = new OpenFileDialog())
            {
                //openFileDialog.InitialDirectory = @"C:\Users\canit\Desktop";
                openFileDialog.Filter = "Image Files|*.jpg;*.jpeg;*.png;*.gif;*.tif;...";

                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    //Get the path of specified file
                    imageFilePath = openFileDialog.FileName;
                    if (File.Exists(PythonDirectory + "test.jpg"))
                    {
                        string timeString = DateTime.Now.ToString("dd_MM_yyyy-HH_mm_ss");
                        string testImagePath = PythonDirectory + "test_date_" + timeString + ".jpg";
                        File.Move(PythonDirectory + "test.jpg", testImagePath);

                    }
                    File.Copy(imageFilePath, PythonDirectory + "test.jpg");

                    pictureBox_Image.Image = new Bitmap(imageFilePath);
                    groupBox2.Visible = true;
                    groupBox4.Visible = true;

                }
            }
        }

        private void btn_StartIdentification_Click(object sender, EventArgs e)
        {
            listBox_Logs.Items.Add("Identification has been started...");
            listBox_Logs.Update();
            Cursor.Current = Cursors.WaitCursor;
            //string PythonFilePath = @"..\..\PythonCode\testing.py"; // It did not work.

            string directory = Directory.GetCurrentDirectory();
            string PythonFilePath = Path.GetFullPath(Path.Combine(directory, @"..\..\")) + @"\PythonCode\testing.py";

            runPythonCode(PythonFilePath, "ArgumanDeneme");

            Cursor.Current = Cursors.Default;
            /*
            using (OpenFileDialog openFileDialog = new OpenFileDialog())
            {
                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    //Get the path of specified file
                    filePath = openFileDialog.FileName;
                    runPythonCode(filePath, "ArgumanDeneme");
                }
            }
            */

        }

        private void runPythonCode(string filenamePython, string args)
        {
            string PythonPath = GetPythonPath();
            //if (string.IsNullOrEmpty(PythonPath))
            //{
            //    listBox_Logs.Items.Add("Python not found in this computer.");
            //    return;
            //}
            ProcessStartInfo pythonProcess = new ProcessStartInfo();
            pythonProcess.FileName = "python.exe";
            pythonProcess.WorkingDirectory = PythonDirectory;
            //pythonProcess.FileName = PythonPath;
            pythonProcess.Arguments = filenamePython + " " + args;
            pythonProcess.UseShellExecute = false;
            pythonProcess.CreateNoWindow = true;
            pythonProcess.RedirectStandardOutput = true;
            pythonProcess.RedirectStandardError = true;

            if (!File.Exists(filenamePython))
            {
                listBox_Logs.Items.Add(filenamePython + " is not exist");
                return;
            }
            using (Process process = Process.Start(pythonProcess))
            {
                using (StreamReader reader = process.StandardOutput)
                {
                    string stderr = process.StandardError.ReadToEnd();
                    string result = reader.ReadToEnd();
                    if (!string.IsNullOrEmpty(stderr))
                    {
                        listBox_Logs.Items.Add("Error/Warning: " + stderr);
                        //Thread t = new Thread(() => MessageBox.Show(result,"Python Output"));
                        //t.Start();
                        //Thread t1 = new Thread(() => MessageBox.Show( stderr, "Error-Warning"));
                        //t1.Start();
                    }
                }
            }
            string timeString = DateTime.Now.ToString("dd_MM_yyyy-HH_mm_ss");
            string imageFileName = PythonDirectory+"outputImage_date_" + timeString + ".jpg";
            if (File.Exists(PythonDirectory+"outputImage.jpg"))
            {
                File.Move(PythonDirectory+"outputImage.jpg", imageFileName);
                pictureBox_Image.Image = new Bitmap(imageFileName);
                listBox_Logs.Items.Add("Identification is successful.");
                listBox_Logs.Items.Add("Text file has been created.");
            }
            else
            {
                listBox_Logs.Items.Add("Identification is not successful!");
                return;
            }

            groupBox3.Visible = true;
            imageAirplane.Visible = true;

            string[] lines = File.ReadAllLines(PythonDirectory + "OCRExport.txt");
 
            foreach (string line in lines) {
                if (line.StartsWith("airSpeed"))
                {
                    string strValue=line.Split(':')[1];
                    row.Cells[1].Value = strValue;
                }else if (line.StartsWith("altimeter"))
                {
                    string strValue=line.Split(':')[1];
                    row3.Cells[1].Value = strValue;
                }
                else if (line.StartsWith("verticalSpeed"))
                {
                    string strValue = line.Split(':')[1];
                    row4.Cells[1].Value = strValue;
                }
                else if (line.StartsWith("horizontalSituation"))
                {
                    string strValue = line.Split(':')[1];
                    row5.Cells[1].Value = strValue;
                }
                else if (line.StartsWith("airplaneName"))
                {
                    string strAirplanename = line.Split(':')[1];
                    if (strAirplanename == "Boeing")
                    {
                        imageAirplane.Image = SeniorProject.Properties.Resources.Boeing;
                        groupBox1.BackgroundImage = SeniorProject.Properties.Resources.BoeingBackground;
                    }
                    if (strAirplanename == "Airbus")
                    {
                        imageAirplane.Image = SeniorProject.Properties.Resources.Airbus;
                        groupBox1.BackgroundImage = SeniorProject.Properties.Resources.AirbusBackground;
                    }
                }
            }
;
        }

        private string GetPythonPath()
        {
            string[] PythonLocations = new string[3] {
                @"HKLM\SOFTWARE\Python\PythonCore\",
                @"HKCU\SOFTWARE\Python\PythonCore\",
                @"HKLM\SOFTWARE\Wow6432Node\Python\PythonCore\"
            };

            foreach (string location in PythonLocations)
            {
                string registerKey = location.Substring(0, 4), path = location.Substring(5);
                RegistryKey theKey = (registerKey == "HKLM" ? Registry.LocalMachine : Registry.CurrentUser);
                RegistryKey theValue = theKey.OpenSubKey(path);
                if (theValue == null)
                    continue;
                foreach (string keyName in theValue.GetSubKeyNames())
                {
                    RegistryKey productKey = theValue.OpenSubKey(keyName);
                    if (productKey != null)
                    {
                        try
                        {
                            string pythonPath = productKey.OpenSubKey("InstallPath").GetValue("ExecutablePath").ToString();
                            if (pythonPath != "")
                                return pythonPath;
                        }
                        catch
                        {

                        }
                    }
                }
            }

            return "";
        }
    }
}
