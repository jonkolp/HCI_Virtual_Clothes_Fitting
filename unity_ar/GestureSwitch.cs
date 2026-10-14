using System;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class GestureSwitch : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;
    public GameObject[] arModels;
    private int currentModelIndex = 0;
    public float rotationSpeedX = 1.0f;
    public float rotationSpeedY = 1.0f; 
    private float lastWristX = 0.5f; 
    private float lastWristY = 0.5f;

    void Start()
    {
        try
        {
            
            client = new TcpClient("localhost", 5000);
            stream = client.GetStream();
            Debug.Log("Connected to Python server");
            SwitchModel(0);
        }
        catch (Exception e)
        {
            Debug.LogError($"Error connecting to Python server: {e.Message}");
        }
    }

    void Update()
    {
        if (stream != null && stream.DataAvailable)
        {
            try
            {
                // Read message from Python server
                byte[] data = new byte[1024];
                int bytesRead = stream.Read(data, 0, data.Length);
                string message = Encoding.UTF8.GetString(data, 0, bytesRead).Trim();

                // Parse the message
                string[] parts = message.Split(',');
                if (parts[0] == "SWITCH_MODEL")
                {
                    SwitchModel((currentModelIndex + 1) % arModels.Length);
                }
                else if (parts[0] == "TRACK_POSITION" && parts.Length == 3)
                {
                    float wristX = float.Parse(parts[1]);
                    float wristY = float.Parse(parts[2]);
                    ApplyRotation(wristX, wristY);
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Error reading from stream: {e.Message}");
            }
        }
    }

    void ApplyRotation(float wristX, float wristY)
    {
        if (arModels[currentModelIndex] != null)
        {
            
            float deltaX = (wristX - lastWristX) * rotationSpeedX;
            float deltaY = (wristY - lastWristY) * rotationSpeedY;

            
            arModels[currentModelIndex].transform.Rotate(Vector3.up, deltaX, Space.World);   
            arModels[currentModelIndex].transform.Rotate(Vector3.right, -deltaY, Space.World);

            
            lastWristX = wristX;
            lastWristY = wristY;
        }
    }

    void SwitchModel(int index)
    {
        
        foreach (GameObject model in arModels)
        {
            model.SetActive(false);
        }
        arModels[index].SetActive(true);
        currentModelIndex = index;
        Debug.Log($"Switched to model {index}");
    }

    void OnApplicationQuit()
    {
        // Close the connection on application quit
        if (stream != null)
        {
            stream.Close();
        }
        if (client != null)
        {
            client.Close();
        }
        Debug.Log("Disconnected from Python server");
    }
}
