import 'package:flutter/material.dart';

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Section
            Text(
              'Welcome to Smart Furnace AI',
              style: TextStyle(
                fontSize: 36,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Advanced Material Synthesis Prediction System',
              style: TextStyle(
                fontSize: 18,
                color: Colors.blueGrey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 48),

            // About Section
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
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.info_outline,
                          size: 32,
                          color: Colors.orange[600],
                        ),
                        const SizedBox(width: 16),
                        Text(
                          'About Our Product',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.blueGrey[900],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Smart Furnace AI is a cutting-edge artificial intelligence platform designed to revolutionize material synthesis processes. Our system uses advanced machine learning algorithms to predict optimal conditions for synthesizing new materials with unprecedented accuracy.',
                      style: TextStyle(
                        fontSize: 16,
                        height: 1.6,
                        color: Colors.grey[700],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),

            // Features Section
            Text(
              'Key Features',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
            const SizedBox(height: 24),

            // Feature Cards Grid
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              mainAxisSpacing: 24,
              crossAxisSpacing: 24,
              childAspectRatio: 1.2,
              children: [
                _FeatureCard(
                  icon: Icons.psychology,
                  title: 'AI-Powered',
                  description:
                      'Machine learning algorithms predict synthesis conditions with high accuracy',
                ),
                _FeatureCard(
                  icon: Icons.flash_on,
                  title: 'Real-Time Analysis',
                  description:
                      'Get instant predictions for your material synthesis experiments',
                ),
                _FeatureCard(
                  icon: Icons.history,
                  title: 'Complete History',
                  description:
                      'Track all your synthesis experiments and their results',
                ),
                _FeatureCard(
                  icon: Icons.precision_manufacturing,
                  title: 'Material Synthesis',
                  description:
                      'Predict optimal temperatures and conditions for any material',
                ),
              ],
            ),
            const SizedBox(height: 48),

            // How It Works Section
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
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.trending_up,
                          size: 32,
                          color: Colors.lightBlue[800],
                        ),
                        const SizedBox(width: 16),
                        Text(
                          'How It Works',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.blueGrey[900],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    _StepItem(
                      step: 1,
                      title: 'Define Your Materials',
                      description:
                          'Enter the base material and target material you want to synthesize',
                    ),
                    const SizedBox(height: 20),
                    _StepItem(
                      step: 2,
                      title: 'Configure Parameters',
                      description:
                          'Optionally specify the target phase or synthesis method',
                    ),
                    const SizedBox(height: 20),
                    _StepItem(
                      step: 3,
                      title: 'Get Predictions',
                      description:
                          'Our AI calculates optimal synthesis conditions including temperature',
                    ),
                    const SizedBox(height: 20),
                    _StepItem(
                      step: 4,
                      title: 'Experiment & Track',
                      description:
                          'Conduct your experiments and track results in your history',
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 48),

            // Technology Stack
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
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.code, size: 32, color: Colors.purple[600]),
                        const SizedBox(width: 16),
                        Text(
                          'Advanced Technology',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.blueGrey[900],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Our platform is built with cutting-edge technologies:',
                      style: TextStyle(fontSize: 16, color: Colors.grey[700]),
                    ),
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        _TechChip('Machine Learning'),
                        _TechChip('Python/Flask'),
                        _TechChip('Real-time Processing'),
                        _TechChip('Cloud Ready'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 64),
          ],
        ),
      ),
    );
  }
}

class _FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;

  const _FeatureCard({
    required this.icon,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 6,
      shadowColor: Colors.black12,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, size: 40, color: Colors.orange[600]),
            const SizedBox(height: 12),
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.blueGrey[900],
              ),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: Text(
                description,
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey[600],
                  height: 1.4,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StepItem extends StatelessWidget {
  final int step;
  final String title;
  final String description;

  const _StepItem({
    required this.step,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: Colors.orange[600],
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              step.toString(),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
          ),
        ),
        const SizedBox(width: 20),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.blueGrey[900],
                ),
              ),
              const SizedBox(height: 4),
              Text(
                description,
                style: TextStyle(fontSize: 14, color: Colors.grey[600]),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _TechChip extends StatelessWidget {
  final String label;

  const _TechChip(this.label);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.lightBlue[50],
        border: Border.all(color: Colors.lightBlue[300]!),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: Colors.lightBlue[900],
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}
