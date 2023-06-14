using System.Collections;
using System.Collections.Generic;
using UnityEngine;

//https://www.youtube.com/playlist?list=PLC8R0n_dfXXr0fc4NdsInilobjVhpXZk4
public class AnimalController : MonoBehaviour
{
    public NeatNetwork myNetwork;

    private float[] sensors;

    private float hitDivider = 20f;
    private float rayDistance = 50f;

    private float overallFitness = 0;

    public int myBrainIndex;

    public int inputNodes, outputNodes, hiddenNodes; // Number of respective nodes for the initial network

    [Range(-1f,1f)]
    public float a,t;

    void Awake()
    {
        sensors = new float[inputNodes];    //Initialize the sensors
    }

    // Update is called once per frame
    void FixedUpdate()
    {
        InputSensors();
        float[] outputs = myNetwork.FeedForwardNetwork(sensors); // Pass in sensor information

        MoveAnimal(outputs[0], outputs[1]);
    }

    private void Death()
    {
        GameObject.FindObjectOfType<NeatGManager>().Death(overallFitness, myBrainIndex);
        Destroy(gameObject);
    }

    private void OnCollisionEnter(Collision other) {
        if(other.transform.tag == "Wall")
        {
            overallFitness = 0;
            Death();
        }
        else if(other.transform.tag == "Plant")
        {
            other.gameObject.GetComponent<PlantController>().SpawnSinglePlant();
            Destroy(other.gameObject);
            overallFitness += 1;
        }
    }

    private void InputSensors()
    {
        Ray r = new Ray(transform.position, transform.up);
        RaycastHit hit;
        if(Physics.Raycast(r, out hit, rayDistance))
        {
            if(hit.transform.tag == "Wall")
            {
                sensors[0] = hit.distance / hitDivider;
                Debug.DrawLine(r.origin, hit.point, Color.white);
            }
        }
        r.direction = (transform.up + transform.right);
        if(Physics.Raycast(r, out hit, rayDistance))
        {
            if(hit.transform.tag == "Wall")
            {
                sensors[1] = hit.distance / hitDivider;
                Debug.DrawLine(r.origin, hit.point, Color.white);
            }
        }
        r.direction = (transform.up - transform.right);
        if(Physics.Raycast(r, out hit, rayDistance))
        {
            if(hit.transform.tag == "Wall")
            {
                sensors[2] = hit.distance / hitDivider;
                Debug.DrawLine(r.origin, hit.point, Color.white);
            }
        }
    }

    public void MoveAnimal(float v, float h)
    {
        // Getting Next Position.
        Vector3 input = Vector3.Lerp(Vector3.zero, new Vector3(0, v * 2f, 0), 0.1f);
        input = transform.TransformDirection(input);

        // Actual Movement of Agent.
        transform.position += input;

        // Rotation of Agent.
        transform.eulerAngles += new Vector3(0, 0, (h*90)*0.1f);
    }
}