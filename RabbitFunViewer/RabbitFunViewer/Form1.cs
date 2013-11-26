using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.ServiceModel;
using Microsoft.Samples.XmlRpc;
using System.Runtime.Serialization;

namespace RabbitFunViewer
{

    [DataContract]
    public struct RabbitGameInfo
    {
        [DataMember]
        public string name;
        [DataMember]
        public int map_size;
        [DataMember]
        public string[] rabbits;
        [DataMember]
        public string info;
        [DataMember]
        public string status;
    }

    [ServiceContract]
    public interface IRabbitsAPI
    {
        [OperationContract(Action = "getRunningGames")]
        RabbitGameInfo[] getRunningGames();
    }

    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {
            timer1.Interval = Convert.ToInt32(textBox2.Text);
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            dataGridView1.Rows.Clear();
            try
            {
                ChannelFactory<IRabbitsAPI> factory = new ChannelFactory<IRabbitsAPI>(new WebHttpBinding(WebHttpSecurityMode.None), textBox1.Text);
                factory.Endpoint.Behaviors.Add(new XmlRpcEndpointBehavior());

                IRabbitsAPI client = factory.CreateChannel();

                foreach (RabbitGameInfo game in client.getRunningGames())
                {
                    dataGridView1.Rows.Add(
                        game.name, 
                        game.map_size.ToString() + "x" + game.map_size.ToString(),
                        String.Join(", ", game.rabbits),
                        game.status,
                        game.info
                   );
                }
                lblError.Text = "";
            }
            catch (Exception ex) {
               lblError.Text = ex.Message;
            }
        }

        private void panel1_Paint(object sender, PaintEventArgs e)
        {

        }

        private void Form1_Load(object sender, EventArgs e)
        {
            timer1_Tick(sender, e);
        }
    }
}
