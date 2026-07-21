import 'package:flutter/material.dart';

class TelemetryScreen extends StatelessWidget {
  final Map<String, dynamic> aiData;

  // This screen REQUIRES the data from the API to open!
  const TelemetryScreen({Key? key, required this.aiData}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Synthesis Telemetry"),
        backgroundColor: Colors.lightBlue[800],
      ),
      body: Center(
        child: Text(
          "Target Temp: ${aiData['optimal_temperature_c']}°C",
          style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
