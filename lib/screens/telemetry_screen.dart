import 'package:flutter/material.dart';

class TelemetryScreen extends StatelessWidget {
  final Map<String, dynamic> aiData;

  // This screen REQUIRES the data from the API to open!
  const TelemetryScreen({Key? key, required this.aiData}) : super(key: key);

  String? _firstString(Map<String, dynamic> data, List<String> keys) {
    for (final key in keys) {
      final value = data[key];
      if (value != null) {
        final text = value.toString().trim();
        if (text.isNotEmpty && text.toLowerCase() != 'null') {
          return text;
        }
      }
    }
    return null;
  }

  Map<String, dynamic> _nestedResult() {
    final nested = aiData['synthesis_result'];
    if (nested is Map) {
      return Map<String, dynamic>.from(nested);
    }
    return const {};
  }

  @override
  Widget build(BuildContext context) {
    final nested = _nestedResult();
    final feasible = aiData['feasible'] == true || nested['feasible'] == true;
    final recommendations =
        aiData['recommendations'] ?? nested['recommendations'];
    final temperature =
        _firstString(aiData, [
          'optimal_temperature_c',
          'optimal_temp_c',
          'required_temperature_c',
        ]) ??
        _firstString(nested, [
          'optimal_temperature_c',
          'optimal_temp_c',
          'required_temperature_c',
        ]);
    final achievableProduct =
        _firstString(aiData, ['achievable_product', 'achievable_compound']) ??
        _firstString(nested, ['achievable_product', 'achievable_compound']);
    final recommendationItems = recommendations is List
        ? recommendations
              .where((item) => item != null)
              .map((item) => item.toString().trim())
              .where((item) => item.isNotEmpty)
              .toList()
        : recommendations is String && recommendations.trim().isNotEmpty
        ? recommendations
              .split(RegExp(r'\r?\n|;'))
              .map((item) => item.trim())
              .where((item) => item.isNotEmpty)
              .toList()
        : <String>[];

    final telemetryBody = feasible
        ? Center(
            child: Text(
              "Target Temp: ${temperature ?? 'N/A'}°C",
              style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
            ),
          )
        : Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 720),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      aiData['message']?.toString() ??
                          nested['message']?.toString() ??
                          'Feasibility check completed.',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    if (aiData['reason'] != null) ...[
                      Text(
                        'Reason',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.blueGrey[900],
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        (aiData['reason'] ?? nested['reason']).toString(),
                        style: const TextStyle(fontSize: 18),
                      ),
                      const SizedBox(height: 12),
                    ],
                    if (achievableProduct != null) ...[
                      Text(
                        'Expected Product',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.blueGrey[900],
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        achievableProduct,
                        style: const TextStyle(fontSize: 18),
                      ),
                      const SizedBox(height: 12),
                    ],
                    if (recommendationItems.isNotEmpty) ...[
                      Text(
                        'Recommendations',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.blueGrey[900],
                        ),
                      ),
                      const SizedBox(height: 6),
                      for (final recommendation in recommendationItems)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: Text(
                            '- $recommendation',
                            style: const TextStyle(fontSize: 18),
                          ),
                        ),
                    ],
                  ],
                ),
              ),
            ),
          );

    return Scaffold(
      appBar: AppBar(
        title: const Text("Synthesis Telemetry"),
        backgroundColor: Colors.lightBlue[800],
      ),
      body: telemetryBody,
    );
  }
}
