import { StyleSheet, Text, View } from 'react-native';

export default function ReservationScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>🏥 予約</Text>
      <Text>予約画面をここに作ります</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
  },
});