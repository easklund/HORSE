package com.example.lofi;

import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

public class MainActivity extends AppCompatActivity {
    private TcpClient mTcpClient;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }


    public void onClickConnect(View view) {
        TextView display = findViewById(R.id.txtDisplay);
        display.setText("Connecting...");

        new ConnectTask().execute();
    }

    public class ConnectTask extends AsyncTask<String, String, TcpClient> {

        @Override
        protected TcpClient doInBackground(String... message) {
            // Update button and textview
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Button btnConnect = findViewById(R.id.btnConnect);
                    TextView txtDisplay = findViewById(R.id.txtDisplay);

                    btnConnect.setText("Disconnect");
                    txtDisplay.setText("Connected...");
                }
            });

            //we create a TCPClient object and
            mTcpClient = new TcpClient(new TcpClient.OnMessageReceived() {
                @Override
                //here the messageReceived method is implemented
                public void messageReceived(String message) {
                    Log.e("TCP", "Got some message");
                    //this method calls the onProgressUpdate
                    publishProgress(message);
                }
            });
            mTcpClient.run();

            return null;
        }

        @Override
        protected void onProgressUpdate(String... values) {
            super.onProgressUpdate(values);

            TextView display = (TextView) findViewById(R.id.txtDisplay);
            display.setText(values[0]);
            //in the arrayList we add the messaged received from server
//            arrayList.add(values[0]);
            // notify the adapter that the data set has changed. This means that new message received
            // from server was added to the list
//            mAdapter.notifyDataSetChanged();
        }
    }
}
