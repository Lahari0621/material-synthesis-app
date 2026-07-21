import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../services/api_service.dart';
import 'telemetry_screen.dart';

class DashboardPage extends StatefulWidget {
  final User user;

  const DashboardPage({required this.user});

  @override
  _DashboardPageState createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  bool _isPhaseSpecific = false;
  bool _isLoading = false;
  String? _errorMessage;

  final TextEditingController _baseMaterialController = TextEditingController();
  final TextEditingController _targetMaterialController =
      TextEditingController();
  final TextEditingController _targetPhaseController = TextEditingController();

  Future<void> _initiateSimulation() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final baseMat = _baseMaterialController.text.trim();
    final targetMat = _targetMaterialController.text.trim();
    final phase = _isPhaseSpecific
        ? _targetPhaseController.text.trim()
        : 'synthesis';

    if (baseMat.isEmpty || targetMat.isEmpty) {
      setState(() {
        _errorMessage = "Base and Target materials are required.";
        _isLoading = false;
      });
      return;
    }

    final result = await ApiService.predictSynthesis(baseMat, targetMat, phase);

    setState(() {
      _isLoading = false;
    });

    if (result.containsKey('error')) {
      setState(() {
        _errorMessage = result['error'];
      });
    } else {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => TelemetryScreen(aiData: result),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Synthesis Dashboard',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Configure your material synthesis parameters and get AI predictions',
              style: TextStyle(fontSize: 16, color: Colors.blueGrey[600]),
            ),
            const SizedBox(height: 48),

            // Main Synthesis Card
            Card(
              elevation: 8,
              shadowColor: Colors.black12,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              color: Colors.white,
              child: Padding(
                padding: const EdgeInsets.all(32.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      "Synthesis Parameters",
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Colors.blueGrey[900],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Mode Toggle
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        FilterChip(
                          label: const Text("Standard Synthesis"),
                          selected: !_isPhaseSpecific,
                          selectedColor: Colors.lightBlue[100],
                          checkmarkColor: Colors.lightBlue[800],
                          onSelected: (bool selected) {
                            setState(() => _isPhaseSpecific = false);
                          },
                        ),
                        const SizedBox(width: 16),
                        FilterChip(
                          label: const Text("Phase-Specific"),
                          selected: _isPhaseSpecific,
                          selectedColor: Colors.orange[100],
                          checkmarkColor: Colors.orange[600],
                          onSelected: (bool selected) {
                            setState(() => _isPhaseSpecific = true);
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 32),

                    // Base Material Input
                    Text(
                      "Base Material",
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: Colors.blueGrey[800],
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _baseMaterialController,
                      decoration: InputDecoration(
                        hintText: "e.g., Iron Oxide (Fe2O3)",
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        prefixIcon: const Icon(Icons.science),
                        prefixIconColor: Colors.orange[600],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Target Material Input
                    Text(
                      "Target Material",
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: Colors.blueGrey[800],
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _targetMaterialController,
                      decoration: InputDecoration(
                        hintText: "e.g., Iron Nanoparticles",
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        prefixIcon: const Icon(Icons.science),
                        prefixIconColor: Colors.orange[600],
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Conditional Phase Input
                    if (_isPhaseSpecific) ...[
                      Text(
                        "Target Phase",
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.blueGrey[800],
                        ),
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _targetPhaseController,
                        decoration: InputDecoration(
                          hintText: "e.g., synthesis, crystalline",
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          prefixIcon: const Icon(Icons.settings),
                          prefixIconColor: Colors.orange[600],
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],

                    // Error Message
                    if (_errorMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red[50],
                          border: Border.all(color: Colors.red[300]!),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(
                            color: Colors.red[700],
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],

                    // Submit Button
                    _isLoading
                        ? const Center(child: CircularProgressIndicator())
                        : ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.orange[600],
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8),
                              ),
                            ),
                            onPressed: _initiateSimulation,
                            child: const Text(
                              "RUN SYNTHESIS PREDICTION",
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                          ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),

            // Info Cards
            Row(
              children: [
                Expanded(
                  child: _InfoCard(
                    icon: Icons.thermostat,
                    title: 'Temperature',
                    description: 'Get optimal synthesis temperature',
                    color: Colors.red[600]!,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _InfoCard(
                    icon: Icons.speed,
                    title: 'Fast',
                    description: 'Instant AI predictions',
                    color: Colors.blue[600]!,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _InfoCard(
                    icon: Icons.verified,
                    title: 'Accurate',
                    description: 'Advanced ML algorithms',
                    color: Colors.green[600]!,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _baseMaterialController.dispose();
    _targetMaterialController.dispose();
    _targetPhaseController.dispose();
    super.dispose();
  }
}

class _InfoCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final Color color;

  const _InfoCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 6,
      shadowColor: Colors.black12,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Icon(icon, size: 36, color: color),
            const SizedBox(height: 12),
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
            const SizedBox(height: 6),
            Text(
              description,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }
}
