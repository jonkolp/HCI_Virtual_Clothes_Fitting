/*
	TUIO C# Demo - part of the reacTIVision project
	Copyright (c) 2005-2016 Martin Kaltenbrunner <martin@tuio.org>

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/

using System;
using System.Drawing;
using System.Windows.Forms;
using System.ComponentModel;
using System.Collections.Generic;
using System.Collections;
using System.Threading;
using TUIO;
using TuioDemo;
using System.IO;
using System.Net.Sockets;
using System.Runtime.InteropServices.ComTypes;
using System.Net;
using System.Threading.Tasks;
using System.Text;
using System.Drawing.Drawing2D;

public class TuioDemo1 : Form, TuioListener
{
	private TuioClient client;
	private Dictionary<long, TuioObject> objectList;
	private Dictionary<long, TuioCursor> cursorList;
	private Dictionary<long, TuioBlob> blobList;

	public static int width, height;
	private int window_width = 640;
	private int window_height = 480;
	private int window_left = 0;
	private int window_top = 0;
	private int screen_width = Screen.PrimaryScreen.Bounds.Width;
	private int screen_height = Screen.PrimaryScreen.Bounds.Height;

	private bool fullscreen;
	private bool verbose;

	Font font = new Font("Arial", 10.0f); int y = 50;
	SolidBrush fntBrush = new SolidBrush(Color.White);
	SolidBrush bgrBrush = new SolidBrush(Color.White);
	SolidBrush curBrush = new SolidBrush(Color.FromArgb(192, 0, 192));
	SolidBrush objBrush = new SolidBrush(Color.FromArgb(64, 0, 0));
	SolidBrush blbBrush = new SolidBrush(Color.FromArgb(64, 64, 64));
	Pen curPen = new Pen(new SolidBrush(Color.Blue), 1);

	int idx = 0; int flag = 0; int flag2 = 0; int CategoryID = 0; int CurrID = -1; bool LogIn = false;int Selected = 1;bool bluetoothSelectionPage = false;int blueMenuOption = 1;string deviceMacAddress;string username;int switchONflag; bool TUIO_or_Mediapipe_page = false;int MPselect = -1;bool stop = true;bool faceDetection = false;
    List<string> Tshirts = new List<string>() { "blackTshirt.PNG", "whiteTshirt.PNG", "blueTshirt.PNG", "greenTshirt.PNG", "redTshirt.PNG" }; // ID = 0
	List<string> LongSleeveShirts = new List<string>() { "blackLongSleeve.PNG", "whiteLongSleeve.PNG" }; // ID = 1
	List<string> Hoodies = new List<string>() { "blueHoodie.PNG", "yellowHoodie.PNG", "greenHoodie.PNG" }; // ID = 2
	List<string> Pants = new List<string>() { "biegePants.PNG", "brownPants.PNG" }; // ID = 3
	List<string> Categories = new List<string>() { "T-shirt", "Long Sleeve", "Hoodies", "Pants" };
	List<string> bluetoothDevices = new List<string>();
	List<List<string>> Price = new List<List<string>>()
		{
			new List<string>(){ "545" , "213", "879", "678", "430" },
			new List<string>(){"150","998"},
			new List<string>(){"300","752","560"},
			new List<string>(){"870","415"}
		};
	public TuioDemo1(int port) {

		verbose = false;
		fullscreen = false;
		width = window_width;
		height = window_height;

		this.ClientSize = new System.Drawing.Size(width, height);
		this.Name = "TuioDemo";
		this.Text = "TuioDemo";

		this.Closing += new CancelEventHandler(Form_Closing);
		this.KeyDown += new KeyEventHandler(Form_KeyDown);

		this.SetStyle(ControlStyles.AllPaintingInWmPaint |
						ControlStyles.UserPaint |
						ControlStyles.DoubleBuffer, true);

		objectList = new Dictionary<long, TuioObject>(128);
		cursorList = new Dictionary<long, TuioCursor>(128);
		blobList = new Dictionary<long, TuioBlob>(128);

		client = new TuioClient(port);
		client.addTuioListener(this);

		client.connect();
	}

	private void Form_KeyDown(object sender, System.Windows.Forms.KeyEventArgs e) {

		if (e.KeyData == Keys.F1) {
			if (fullscreen == false) {

				width = screen_width;
				height = screen_height;

				window_left = this.Left;
				window_top = this.Top;

				this.FormBorderStyle = FormBorderStyle.None;
				this.Left = 0;
				this.Top = 0;
				this.Width = screen_width;
				this.Height = screen_height;

				fullscreen = true;
			} else {

				width = window_width;
				height = window_height;

				this.FormBorderStyle = FormBorderStyle.Sizable;
				this.Left = window_left;
				this.Top = window_top;
				this.Width = window_width;
				this.Height = window_height;

				fullscreen = false;
			}
		} else if (e.KeyData == Keys.Escape) {
			this.Close();

		} else if (e.KeyData == Keys.V) {
			verbose = !verbose;
		}

	}

	private void Form_Closing(object sender, System.ComponentModel.CancelEventArgs e)
	{
		client.removeTuioListener(this);

		client.disconnect();
		System.Environment.Exit(0);
	}

	public void addTuioObject(TuioObject o)
	{
		lock (objectList)
		{
			objectList.Add(o.SessionID, o);
		} if (verbose) Console.WriteLine("add obj " + o.SymbolID + " (" + o.SessionID + ") " + o.X + " " + o.Y + " " + o.Angle);
	}
	// Rotation
	public void updateTuioObject(TuioObject o)
	{
		try
		{
			// Convert the angle from radians to degrees
			float angleDegrees = (float)(o.Angle * 180.0 / Math.PI);

			if (verbose)
			{
				Console.WriteLine($"set obj {o.SymbolID} {o.SessionID} {o.X} {o.Y} {o.Angle} {o.MotionSpeed} {o.RotationSpeed} {o.MotionAccel} {o.RotationAccel}");
			}

			// Handle right rotation (angle between 5 and 15 degrees)
			if (angleDegrees >= 5 && angleDegrees <= 15)
			{
				if (flag == 0)
				{
					flag = 1;

					// Safely increment idx and wrap around
					idx++;
					List<string> currentCategory = GetCategoryItems(CategoryID);
					if (idx >= currentCategory.Count)
					{
						idx = 0; // Wrap to the first item
					}

					Console.WriteLine($"Right rotation detected. Updated idx: {idx}");
					flag = 2; // Prevent repeated updates
					if (Selected != -1) { Selected = Selected == 1 ? 2 : 1; }
					if (TUIO_or_Mediapipe_page) { MPselect = MPselect == 1 ? 0 : 1; }
					if (bluetoothDevices.Count > 0) { blueMenuOption++; blueMenuOption = blueMenuOption > bluetoothDevices.Count ? 1: blueMenuOption; }
				}

				this.Text = "right";
			}
			// Handle left rotation (angle between 345 and 355 degrees)
			else if (angleDegrees >= 345 && angleDegrees <= 355)
			{
				if (flag2 == 0)
				{
					flag2 = 1;

					// Safely increment the category and wrap around
					CategoryID = (CategoryID + 1) % Categories.Count;

					// Reset the index for the new category
					idx = 0;
					Console.WriteLine($"Left rotation detected. Updated CategoryID: {CategoryID}");

					flag2 = 2; // Prevent repeated updates
					if (Selected == 1 && !bluetoothSelectionPage) { Bluetooth(); }else if (Selected == 2) {  faceDetection = true; Face_detection();  }
					if (bluetoothSelectionPage) { sendIndex(blueMenuOption); }
					if (TUIO_or_Mediapipe_page && MPselect != -1 && !stop) { switchONflag = MPselect == 1 ? 0 : 1;TUIO_or_Mediapipe(); }
                }

				//MessageBox.Show("left");
			}
			else
			{
				// Reset flags if no significant rotation angle is detected
				flag = 0;
				flag2 = 0;
			}

			// Debug output for current state
			Console.WriteLine($"CategoryID: {CategoryID}, idx: {idx}, angleDegrees: {angleDegrees}");
		}
		catch (Exception ex)
		{
			Console.WriteLine($"Error in updateTuioObject: {ex.Message}");
			Console.WriteLine(ex.StackTrace);
		}
	}
    private List<string> GetCategoryItems(int categoryId)
    {
        try
        {
            switch (categoryId)
            {
                case 0:
                    return Tshirts;
                case 1:
                    return LongSleeveShirts;
                case 2:
                    return Hoodies;
                case 3:
                    return Pants;
                default:
                    return new List<string>(); // Return an empty list if categoryId is invalid
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error in GetCategoryItems: {ex.Message}");
            return new List<string>(); // Fallback to empty list
        }
    }





    public void removeTuioObject(TuioObject o) {
			lock(objectList) {
				objectList.Remove(o.SessionID);
			}
			if (verbose) Console.WriteLine("del obj "+o.SymbolID+" ("+o.SessionID+")");
		}

		public void addTuioCursor(TuioCursor c) {
			lock(cursorList) {
				cursorList.Add(c.SessionID,c);
			}
			if (verbose) Console.WriteLine("add cur "+c.CursorID + " ("+c.SessionID+") "+c.X+" "+c.Y);
		}

		public void updateTuioCursor(TuioCursor c) {
			if (verbose) Console.WriteLine("set cur "+c.CursorID + " ("+c.SessionID+") "+c.X+" "+c.Y+" "+c.MotionSpeed+" "+c.MotionAccel);
		}

		public void removeTuioCursor(TuioCursor c) {
			lock(cursorList) {
				cursorList.Remove(c.SessionID);
			}
			if (verbose) Console.WriteLine("del cur "+c.CursorID + " ("+c.SessionID+")");
 		}

		public void addTuioBlob(TuioBlob b) {
			lock(blobList) {
				blobList.Add(b.SessionID,b);
			}
			if (verbose) Console.WriteLine("add blb "+b.BlobID + " ("+b.SessionID+") "+b.X+" "+b.Y+" "+b.Angle+" "+b.Width+" "+b.Height+" "+b.Area);
		}

		public void updateTuioBlob(TuioBlob b) {
		
			if (verbose) Console.WriteLine("set blb "+b.BlobID + " ("+b.SessionID+") "+b.X+" "+b.Y+" "+b.Angle+" "+b.Width+" "+b.Height+" "+b.Area+" "+b.MotionSpeed+" "+b.RotationSpeed+" "+b.MotionAccel+" "+b.RotationAccel);
		}

		public void removeTuioBlob(TuioBlob b) {
			lock(blobList) {
				blobList.Remove(b.SessionID);
			}
			if (verbose) Console.WriteLine("del blb "+b.BlobID + " ("+b.SessionID+")");
		}

		public void refresh(TuioTime frameTime) {
			Invalidate();
		}
    public void Bluetooth(string host = "127.0.0.1", int port = 65432)
    {
        TcpListener Listener = new TcpListener(IPAddress.Any, port);
        Listener.Start();
		Text="Started listening";

        Task.Run(async () =>
        {
            try
            {
                while (true)
                {
                    using (TcpClient client = await Listener.AcceptTcpClientAsync())
                    using (NetworkStream stream = client.GetStream())
                    {
                        byte[] buffer = new byte[4096];
                        int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
                        string deviceList = System.Text.Encoding.ASCII.GetString(buffer, 0, bytesRead).Trim();

                        // Split the device list string into individual device names using newline as the delimiter
                        List<string> devices = new List<string>(deviceList.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.RemoveEmptyEntries));
						bluetoothDevices = devices;
						Selected = 0;

                        //Invoke(new Action(() =>
                        //{
                        //    MessageBox.Show("Devices: "+ string.Join("\n",devices));
                            
                        //}));
						bluetoothSelectionPage = true;

                        break;
					}
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error: " + ex.Message);
            }
			finally
			{
				Listener.Stop();
			}
        });
    }
	public void sendIndex(int selectedIndex, string host = "127.0.0.1", int port = 65432)
	{
		try
		{
			using (TcpClient client = new TcpClient(host, port))
			using (NetworkStream stream = client.GetStream())
			{
				// Send the selected index
				byte[] selectedIndexBytes = Encoding.ASCII.GetBytes(selectedIndex.ToString());
				stream.Write(selectedIndexBytes, 0, selectedIndexBytes.Length);

				// Read the MAC address of the selected device
				byte[] buffer = new byte[4096];
				int bytesRead = stream.Read(buffer, 0, buffer.Length);
				string macAddress = Encoding.ASCII.GetString(buffer, 0, bytesRead).Trim();
				deviceMacAddress = macAddress;

                // Show the MAC address in a message box
                Text="Selected Device MAC Address: " + macAddress;
				FindUserByMac();
				
				bluetoothSelectionPage = false;
				TUIO_or_Mediapipe_page = true;
				Selected = -1;
				this.Refresh();
                return;
            }
		}
		catch (Exception ex)
		{
			MessageBox.Show("Error in sendIndex: " + ex.Message);
		}

	}
	public void TUIO_or_Mediapipe(string host = "127.0.0.1", int port = 50000)
	{
        try
        {
            using (TcpClient client = new TcpClient(host, port))
            using (NetworkStream stream = client.GetStream())
            {
                // Send the flag
                byte[] selectedIndexBytes = Encoding.ASCII.GetBytes(switchONflag.ToString());
                stream.Write(selectedIndexBytes, 0, selectedIndexBytes.Length);

				if (switchONflag == 1)
				{
					this.Close();
				}

				LogIn = true;
				TUIO_or_Mediapipe_page = false;



                return;
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error in TUIO_or_Mediapipe function: " + ex.Message);
        }
    }
	public void Face_detection(string host = "127.0.0.1", int port = 12345)
	{
        try
        {
            using (TcpClient client = new TcpClient(host, port))
            using (NetworkStream stream = client.GetStream())
            {
				// Send the flag
				int f = 1;
                byte[] flagg = Encoding.ASCII.GetBytes(f.ToString());
                stream.Write(flagg, 0, flagg.Length);
				LogIn = true;
				username = "mahmoud";
				faceDetection = false;
				//ListenForFaceDetection();
                return;
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error in face deteciton: " + ex.Message);
        }
    }
	public void ListenForFaceDetection(int port=12346)
	{
        TcpListener Listener = new TcpListener(IPAddress.Any, port);
        Listener.Start();
        MessageBox.Show("Started listening for user name");

        Task.Run(async () =>
        {
            try
            {
                while (true)
                {
                    using (TcpClient client = await Listener.AcceptTcpClientAsync())
                    using (NetworkStream stream = client.GetStream())
                    {
                        byte[] buffer = new byte[4096];
                        int bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length);
                        string user = System.Text.Encoding.ASCII.GetString(buffer, 0, bytesRead).Trim();

                        
                        username = user;

                        Invoke(new Action(() =>
                        {
                            MessageBox.Show($"User Name: {user}");

                        }));
						LogIn = true;
						faceDetection = false;
                        break;
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error in ListenForFaceDetection: " + ex.Message);
            }
            finally
            {
                Listener.Stop();
            }
        });
    }
    public void FindUserByMac()
    {
		
        try
        {
            // Read all lines from the file
            string[] lines = File.ReadAllLines("MACAddress.txt");

            foreach (string line in lines)
            {
                // Skip empty lines
                if (string.IsNullOrWhiteSpace(line)) continue;

                // Split the line into name and address
                string[] parts = line.Split(',');

                if (parts.Length == 2)
                {
                    string name = parts[0].Trim();
                    string macAddress = parts[1].Trim();

                    // Compare the MAC address
                    if (macAddress.Equals(deviceMacAddress, StringComparison.OrdinalIgnoreCase))
                    {
                        username= name; //  name if MAC matches
						return;
                    }
                }
                else
                {
                    MessageBox.Show($"Invalid line format: {line}");
                }
            }

            MessageBox.Show ("No user found with the provided MAC address."); username = "Guest";
        }
        catch (FileNotFoundException)
        {
            MessageBox.Show ($"Error: File not found at {"MACAddress.txt"}.");
        }
        catch (Exception ex)
        {
            MessageBox.Show ($"An error occurred: {ex.Message}");
        }
    }
    protected override void OnPaintBackground(PaintEventArgs pevent) ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
		{
			// Getting the graphics object
			Graphics g = pevent.Graphics;
			g.FillRectangle(bgrBrush, new Rectangle(0,0,width,height));
		if (LogIn)
		{
			// Home Page
			try // background image
			{
				Bitmap backgroundImage = new Bitmap("abdul.jpg");
				g.DrawImage(backgroundImage, new Rectangle(0, 0, width, height));
			}
			catch (Exception ex)
			{

				Console.WriteLine("Error loading background image: " + ex.Message);
				g.FillRectangle(bgrBrush, new Rectangle(0, 0, width, height));
			}
			Font font = new Font("Arial", 20, FontStyle.Bold); y = 50;
			g.DrawString("Welcome " + username, font, Brushes.Blue, 0, 0);
			for (int i = 0; i < 4; i++)
			{
				SolidBrush brsh = new SolidBrush(Color.White);

				if (CategoryID == i) { brsh = new SolidBrush(Color.Yellow); }
				g.FillRectangle(brsh, 0, y, 170, 50);
				g.DrawString(Categories[i], font, Brushes.Black, 0, y);
				y += 100;
			}
		}
		else if(!bluetoothSelectionPage && !TUIO_or_Mediapipe_page && !faceDetection)
		{
			/*Log in page

					Font f = new Font("Arial", 12, FontStyle.Bold);
			g.DrawString("Welcome to Virtual Fitting Room\nChoose how to Log in", f, Brushes.Black, 100, 100);

			//g.DrawString("Choose how you want to LogIn", f, Brushes.Black, 100, 130);
			SolidBrush brsh1 = new SolidBrush(Color.Blue);
			SolidBrush brsh2 = new SolidBrush(Color.Orange);
			g.FillRectangle(Selected == 1 ? brsh2 : brsh1, ClientSize.Width / 3, ClientSize.Height / 2 - 25, 140, 50);
			g.FillRectangle(Selected == 2 ? brsh2 : brsh1, (ClientSize.Width / 3) * 2, ClientSize.Height / 2 - 25, 140, 50);

			g.DrawString("Bluetooth", f, Brushes.White, ClientSize.Width / 3, (ClientSize.Height / 2 - 25) + 50 / 2);
			g.DrawString("Face Detection", f, Brushes.White, (ClientSize.Width / 3) * 2, (ClientSize.Height / 2 - 25) + 50 / 2);

			g.DrawString("Rotate right to select\nRotate left to confirm selection (Orange is selected)", f, Brushes.Black, 100, 300);
			Log in page
			Log in page
		   Graphics g = this.CreateGraphics();*/
			g.Clear(Color.FromArgb(240, 240, 240)); // Light gray background

            // Fonts
            Font titleFont = new Font("Segoe UI", 18, FontStyle.Bold);
            Font optionFont = new Font("Segoe UI", 12, FontStyle.Regular);
            Font instructionFont = new Font("Segoe UI", 10, FontStyle.Italic);

            // Title
            g.DrawString("Welcome to Virtual Fitting Room", titleFont, Brushes.Black, 100, 40);
            g.DrawString("Choose how to Log in", new Font("Segoe UI", 14, FontStyle.Regular), Brushes.Black, 100, 80);

            // Define colors
            Color buttonBaseColor = Color.FromArgb(0, 122, 204); // Blue
            Color buttonSelectedColor = Color.FromArgb(255, 140, 0); // Orange
            Color buttonBorderColor = Color.FromArgb(200, 200, 200); // Light gray
            Color shadowColor = Color.FromArgb(100, 0, 0, 0); // Semi-transparent black for shadow

            // Create brushes and pens
            SolidBrush baseBrush = new SolidBrush(buttonBaseColor);
            SolidBrush selectedBrush = new SolidBrush(buttonSelectedColor);
            Pen borderPen = new Pen(buttonBorderColor, 2);
            SolidBrush shadowBrush = new SolidBrush(shadowColor);

            // Button dimensions and positions
            int buttonWidth = 160;
            int buttonHeight = 60;
            int buttonY = ClientSize.Height / 2 - 50;
            int spacing = 50;

            // Button rectangles
            Rectangle bluetoothButton = new Rectangle(ClientSize.Width / 2 - buttonWidth - spacing / 2, buttonY, buttonWidth, buttonHeight);
            Rectangle faceDetectionButton = new Rectangle(ClientSize.Width / 2 + spacing / 2, buttonY, buttonWidth, buttonHeight);

            // Draw shadows
            g.FillRectangle(shadowBrush, bluetoothButton.X + 4, bluetoothButton.Y + 4, buttonWidth, buttonHeight);
            g.FillRectangle(shadowBrush, faceDetectionButton.X + 4, faceDetectionButton.Y + 4, buttonWidth, buttonHeight);

            // Draw buttons with gradient effect
            using (LinearGradientBrush bluetoothGradient = new LinearGradientBrush(bluetoothButton,
                Selected == 1 ? buttonSelectedColor : buttonBaseColor, Color.White, 45F))
            {
                g.FillRectangle(bluetoothGradient, bluetoothButton);
            }
            using (LinearGradientBrush faceDetectionGradient = new LinearGradientBrush(faceDetectionButton,
                Selected == 2 ? buttonSelectedColor : buttonBaseColor, Color.White, 45F))
            {
                g.FillRectangle(faceDetectionGradient, faceDetectionButton);
            }

            // Draw button borders
            g.DrawRectangle(borderPen, bluetoothButton);
            g.DrawRectangle(borderPen, faceDetectionButton);

            // Draw button text
            StringFormat textFormat = new StringFormat();
            textFormat.Alignment = StringAlignment.Center;
            textFormat.LineAlignment = StringAlignment.Center;

            g.DrawString("Bluetooth", optionFont, Brushes.White, bluetoothButton, textFormat);
            g.DrawString("Face Detection", optionFont, Brushes.White, faceDetectionButton, textFormat);

            // Instructions
            g.DrawString("Rotate right to select\nRotate left to confirm selection (Orange is selected)",
                instructionFont, Brushes.Black, 100, buttonY + buttonHeight + 60);


        }
        else if (bluetoothSelectionPage && !TUIO_or_Mediapipe_page && !faceDetection)
		{
            // Bluetooth selection page
            //int y = 100;

            //if (bluetoothDevices.Count > 0)
            //{
            //	for (int i = 1;i < bluetoothDevices.Count + 1;i++)
            //	{
            //		if (i == blueMenuOption) { g.FillRectangle(Brushes.Blue, 100, y, 150, 30); }
            //		g.DrawString($"{i}. {bluetoothDevices[i-1]}", font, Brushes.Black, 100, y);
            //		y += 50;
            //	}
            //}
            // Bluetooth Selection Page

            g.Clear(Color.FromArgb(240, 240, 240)); // Light gray background

            // Fonts and Colors
            Font titleFont = new Font("Segoe UI", 16, FontStyle.Bold);
            Font deviceFont = new Font("Segoe UI", 12, FontStyle.Regular);
            Font selectedFont = new Font("Segoe UI", 12, FontStyle.Bold);
            Color itemBaseColor = Color.FromArgb(200, 200, 200); // Light gray
            Color selectedItemColor = Color.FromArgb(70, 130, 180); // Steel Blue
            Color textColor = Color.Black;
            Color selectedTextColor = Color.White;

            // Title
            g.DrawString("Bluetooth Device Selection", titleFont, Brushes.Black, 100, 20);

            int y = 100;
            int x = 100;
            int itemWidth = 250;
            int itemHeight = 40;
            int spacing = 10;

            // Check if devices are available
            if (bluetoothDevices.Count > 0)
            {
                for (int i = 1; i <= bluetoothDevices.Count; i++)
                {
                    // Define item rectangle
                    Rectangle itemRectangle = new Rectangle(x, y, itemWidth, itemHeight);

                    // Draw background for selected or unselected items
                    SolidBrush backgroundBrush = (i == blueMenuOption)
                        ? new SolidBrush(selectedItemColor)
                        : new SolidBrush(itemBaseColor);

                    g.FillRectangle(backgroundBrush, itemRectangle);

                    // Draw border for the item
                    g.DrawRectangle(Pens.Gray, itemRectangle);

                    // Draw item text
                    StringFormat textFormat = new StringFormat
                    {
                        Alignment = StringAlignment.Near,
                        LineAlignment = StringAlignment.Center
                    };

                    g.DrawString(
                        $"{i}. {bluetoothDevices[i - 1]}",
                        i == blueMenuOption ? selectedFont : deviceFont,
                        new SolidBrush(i == blueMenuOption ? selectedTextColor : textColor),
                        itemRectangle,
                        textFormat);

                    y += itemHeight + spacing;
                }
            }
            else
            {
                // Display message if no devices are available
                g.DrawString("No Bluetooth devices found.", deviceFont, Brushes.Black, x, y);
            }

        }
        else if(TUIO_or_Mediapipe_page && !faceDetection)
		{
			// TUIO or Mediapipe Selection Page
			stop = MPselect != -1 ? false : true;
			MPselect = MPselect == -1 ? 1 : MPselect;
            Font f = new Font("Arial", 12, FontStyle.Bold);
            g.DrawString($"Welcome {username}\nChoose one", f, Brushes.Black, 100, 100);

            //g.DrawString("Choose how you want to LogIn", f, Brushes.Black, 100, 130);
            SolidBrush brsh1 = new SolidBrush(Color.Blue);
            SolidBrush brsh2 = new SolidBrush(Color.Orange);
            g.FillRectangle(MPselect == 1 ? brsh2 : brsh1, ClientSize.Width / 3, ClientSize.Height / 2 - 25, 140, 50);
            g.FillRectangle(MPselect == 0 ? brsh2 : brsh1, (ClientSize.Width / 3) * 2, ClientSize.Height / 2 - 25, 140, 50);

            g.DrawString("TUIO", f, Brushes.White, ClientSize.Width / 3, (ClientSize.Height / 2 - 25) + 50 / 2);
            g.DrawString("Mediapipe", f, Brushes.White, (ClientSize.Width / 3) * 2, (ClientSize.Height / 2 - 25) + 50 / 2);

            g.DrawString("Rotate right to select\nRotate left to confirm selection (Orange is selected)", f, Brushes.Black, 100, 300);
        }
		else
		{
            /* Face Detection */
            Font f = new Font("Arial", 30, FontStyle.Bold);
            g.DrawString("Please Look at the camera for face detection", f, Brushes.Black, 100, 300);

        }
        //g.DrawString(Price[CategoryID][idx], font, Brushes.White, 0, y);
        // draw the cursor path
        if (cursorList.Count > 0) {
 			 lock(cursorList) {
			 foreach (TuioCursor tcur in cursorList.Values) {
					List<TuioPoint> path = tcur.Path;
					TuioPoint current_point = path[0];

					for (int i = 0; i < path.Count; i++) {
						TuioPoint next_point = path[i];
						g.DrawLine(curPen, current_point.getScreenX(width), current_point.getScreenY(height), next_point.getScreenX(width), next_point.getScreenY(height));
						current_point = next_point;
					}
					g.FillEllipse(curBrush, current_point.getScreenX(width) - height / 100, current_point.getScreenY(height) - height / 100, height / 50, height / 50);
					g.DrawString(tcur.CursorID + "", font, fntBrush, new PointF(tcur.getScreenX(width) - 10, tcur.getScreenY(height) - 10));
				}
			}
		 }

			// draw the objects
			if (objectList.Count > 0) {
 				lock(objectList) {
					foreach (TuioObject tobj in objectList.Values) {
						int ox = tobj.getScreenX(width);
						int oy = tobj.getScreenY(height);
						int size = height / 10;

						string img_path = "";
						if (CurrID == -1) { CurrID = tobj.SymbolID; CategoryID = tobj.SymbolID; }
						if(flag2 == 0 && CurrID != tobj.SymbolID){ CategoryID = tobj.SymbolID; }
					if (LogIn)
					{
						switch (CategoryID)
						{
							case 0: // T-shirts
								if (idx > Tshirts.Count - 1) { idx = 0; }
								img_path = Tshirts[idx];
								break;
							case 1: // Long Sleeve
								if (idx > LongSleeveShirts.Count - 1) { idx = 0; }
								img_path = LongSleeveShirts[idx];
								break;
							case 2: // Hoodies
								if (idx > Hoodies.Count - 1) { idx = 0; }
								img_path = Hoodies[idx];
								break;
							case 3: // Pants
								if (idx > Pants.Count - 1) { idx = 0; }
								img_path = Pants[idx];
								break;
							default:
								if (idx > Tshirts.Count - 1) { idx = 0; }
								img_path = Tshirts[idx];
								break;

						}
					}
					else
					{
						if(tobj.SymbolID >=0 && tobj.SymbolID <= 215)
						{

						}
					}
						g.TranslateTransform(ox, oy);
						g.RotateTransform((float)(tobj.Angle / Math.PI * 180.0f));
						g.TranslateTransform(-ox, -oy);
					CurrID = tobj.SymbolID;
					try
					{
						if (!File.Exists(img_path))
						{
							Console.WriteLine($"Image file not found: {img_path}");
							return;
						}

						using (Bitmap img = new Bitmap(img_path))
						{
							g.DrawImage(img, ox, oy, img.Width / 7, img.Height / 7);
						}

						g.TranslateTransform(ox, oy);
						g.RotateTransform(-1 * (float)(tobj.Angle / Math.PI * 180.0f));
						g.TranslateTransform(-ox, -oy);
					}
					catch (OutOfMemoryException ex)
					{
						Console.WriteLine($"Error loading image: {ex.Message}");
					}
					catch (Exception ex)
					{
						Console.WriteLine($"Unexpected error: {ex.Message}");
					}

				}
			}
			}

			// draw the blobs
			if (blobList.Count > 0) {
				lock(blobList) {
					foreach (TuioBlob tblb in blobList.Values) {
						int bx = tblb.getScreenX(width);
						int by = tblb.getScreenY(height);
						float bw = tblb.Width*width;
						float bh = tblb.Height*height;

						g.TranslateTransform(bx, by);
						g.RotateTransform((float)(tblb.Angle / Math.PI * 180.0f));
						g.TranslateTransform(-bx, -by);

						g.FillEllipse(blbBrush, bx - bw / 2, by - bh / 2, bw, bh);

						g.TranslateTransform(bx, by);
						g.RotateTransform(-1 * (float)(tblb.Angle / Math.PI * 180.0f));
						g.TranslateTransform(-bx, -by);
						
						g.DrawString(tblb.BlobID + "", font, fntBrush, new PointF(bx, by));
					}
				}
			}
		}

		public static void Main(String[] argv) {
	 		int port = 0;
			switch (argv.Length) {
				case 1:
					port = int.Parse(argv[0],null);
					if(port==0) goto default;
					break;
				case 0:
					port = 3333;
					break;
				default:
					Console.WriteLine("usage: mono TuioDemo [port]");
					System.Environment.Exit(0);
					break;
			}
			
			TuioDemo1 app = new TuioDemo1(port);
			Application.Run(app);
		}
	}
