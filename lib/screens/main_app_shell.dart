import 'package:flutter/material.dart';
import '../models/user_model.dart';
import 'home_page.dart';
import 'dashboard_page.dart';
import 'settings_page.dart';
import 'history_page.dart';

class MainAppShell extends StatefulWidget {
  final User user;

  const MainAppShell({required this.user});

  @override
  _MainAppShellState createState() => _MainAppShellState();
}

class _MainAppShellState extends State<MainAppShell> {
  int _selectedIndex = 0;

  late final List<Widget> _pages;

  @override
  void initState() {
    super.initState();
    _pages = [
      HomePage(),
      DashboardPage(user: widget.user),
      HistoryPage(),
      SettingsPage(user: widget.user),
    ];
  }

  void _onNavItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Sidebar Navigation
          NavigationRail(
            selectedIndex: _selectedIndex,
            onDestinationSelected: _onNavItemTapped,
            labelType: NavigationRailLabelType.all,
            backgroundColor: Colors.blueGrey[900],
            selectedIconTheme: const IconThemeData(
              color: Colors.orange,
              size: 28,
            ),
            selectedLabelTextStyle: const TextStyle(
              color: Colors.orange,
              fontWeight: FontWeight.bold,
            ),
            unselectedIconTheme: const IconThemeData(
              color: Colors.grey,
              size: 24,
            ),
            unselectedLabelTextStyle: const TextStyle(color: Colors.grey),
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.home_outlined),
                selectedIcon: Icon(Icons.home),
                label: Text('Home'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.dashboard_outlined),
                selectedIcon: Icon(Icons.dashboard),
                label: Text('Dashboard'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.history_outlined),
                selectedIcon: Icon(Icons.history),
                label: Text('History'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.settings_outlined),
                selectedIcon: Icon(Icons.settings),
                label: Text('Settings'),
              ),
            ],
          ),
          // Main Content Area
          Expanded(
            child: Container(
              color: Colors.grey[50],
              child: _pages[_selectedIndex],
            ),
          ),
        ],
      ),
    );
  }
}
