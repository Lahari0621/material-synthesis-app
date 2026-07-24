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

  void _onNavItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  List<Widget> get _activePages {
    return [
      HomePage(),
      DashboardPage(user: widget.user),
      HistoryPage(user: widget.user),
      SettingsPage(user: widget.user),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final isCompact = MediaQuery.of(context).size.width < 900;

    if (isCompact) {
      return Scaffold(
        body: Container(
          color: Colors.grey[50],
          child: _activePages[_selectedIndex],
        ),
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: _selectedIndex,
          onTap: _onNavItemTapped,
          type: BottomNavigationBarType.fixed,
          selectedItemColor: Colors.orange[700],
          unselectedItemColor: Colors.blueGrey[500],
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_outlined),
              activeIcon: Icon(Icons.home),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.dashboard_outlined),
              activeIcon: Icon(Icons.dashboard),
              label: 'Dashboard',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.history_outlined),
              activeIcon: Icon(Icons.history),
              label: 'History',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.settings_outlined),
              activeIcon: Icon(Icons.settings),
              label: 'Settings',
            ),
          ],
        ),
      );
    }

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
              child: _activePages[_selectedIndex],
            ),
          ),
        ],
      ),
    );
  }
}
