
import { useEffect, useState } from 'react';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';

type Pet = {
  id: number;
  name: string;
  type: string;
  age: number | null;
  weight: number | null;
  note: string;
  photo: string | null;
};

export default function HomeScreen() {
  const [pets, setPets] = useState<Pet[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/pets')
      .then((response) => response.json())
      .then((data) => {
        setPets(data.pets);
        setLoading(false);
      })
      .catch((error) => {
        console.error('ペット情報の取得に失敗:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" />
        <Text>読み込み中...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🐾 ペット一覧</Text>

      {pets.map((pet) => (
        <View key={pet.id} style={styles.petCard}>
          <Text style={styles.name}>{pet.name}</Text>
          <Text>種類：{pet.type}</Text>
          <Text>年齢：{pet.age ?? '未登録'}</Text>
          <Text>体重：{pet.weight ?? '未登録'}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 24,
  },
  petCard: {
    padding: 20,
    borderWidth: 1,
    borderRadius: 12,
    marginBottom: 12,
  },
  name: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 8,
  },
});