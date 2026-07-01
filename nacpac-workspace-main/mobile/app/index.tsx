import { View, Text, Switch, StyleSheet } from 'react-native';
import { useState } from 'react';

export default function HomeScreen() {
  const [darkMode, setDarkMode] = useState(false);

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: darkMode ? '#0f0e17' : '#ffffff',
      padding: 20,
      justifyContent: 'center',
    },
    title: {
      fontSize: 28,
      fontWeight: 'bold',
      color: darkMode ? '#e8e6f0' : '#1a1625',
      marginBottom: 20,
    },
    toggleContainer: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: 15,
      paddingHorizontal: 15,
      backgroundColor: darkMode ? '#1a1829' : '#f4f2ff',
      borderRadius: 10,
      marginBottom: 20,
    },
    toggleLabel: {
      fontSize: 16,
      fontWeight: '600',
      color: darkMode ? '#b8a8d8' : '#5a3493',
    },
    description: {
      fontSize: 14,
      color: darkMode ? '#8b7ca8' : '#6b5e8a',
      lineHeight: 22,
    },
  });

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📱 Nacpac</Text>

      <View style={styles.toggleContainer}>
        <Text style={styles.toggleLabel}>🌙 Dark Mode</Text>
        <Switch
          value={darkMode}
          onValueChange={setDarkMode}
          trackColor={{ false: '#ddd8f0', true: '#4a4660' }}
          thumbColor={darkMode ? '#5a3493' : '#f5b11b'}
        />
      </View>

      <Text style={styles.description}>
        Welcome to the Nacpac Admin App. Toggle dark mode above to see the theme change in real-time.
      </Text>
    </View>
  );
}
