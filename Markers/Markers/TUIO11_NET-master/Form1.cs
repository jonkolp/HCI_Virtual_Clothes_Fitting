using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement.Rebar;

namespace TuioDemo
{
    public partial class Form1 : Form
    {
        Bitmap off;
        public Form1()
        {
            Paint += Form1_Paint;
            Load += Form1_Load;
            this.Size = new Size(800, 600);
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            off = new Bitmap(this.ClientSize.Width, this.ClientSize.Height);
        }

        private void Form1_Paint(object sender, PaintEventArgs e)
        {
            DrawDubb(e.Graphics);
        }

        public void DrawScene(Graphics g)
        {
            g.Clear(Color.White);

            Font f = new Font("Arial", 12, FontStyle.Bold);
            Pen p=new Pen(Brushes.SkyBlue, 5);

            g.DrawString("Welcome", f, Brushes.Black, 100, 100);
            g.FillRectangle(Brushes.Blue, ClientSize.Width / 2, ClientSize.Height / 2, 100, 50);

        }
        public void DrawDubb(Graphics g)
        {
            Graphics g2 = Graphics.FromImage(off);
            DrawScene(g2);
            g.DrawImage(off, 0, 0);
        }
    }
}
