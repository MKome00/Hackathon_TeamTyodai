import { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

type Pet = {
  id: number;
  name: string;
  type: string;
  age: number | null;
  weight: number | null;
  note: string;
  photo: string | null;
};

const API_BASE_URL = 'http://127.0.0.1:5000';

export default function PetsScreen() {
  const [pets, setPets] = useState<Pet[]>([]);
  const [selectedPet, setSelectedPet] = useState<Pet | null>(null);
  const [viewMode, setViewMode] = useState<'profile' | 'list'>('profile');

  const [name, setName] = useState('');
  const [type, setType] = useState('');
  const [age, setAge] = useState('');
  const [weight, setWeight] = useState('');
  const [note, setNote] = useState('');

  const [loading, setLoading] = useState(true);

  // -----------------------------
  // ペット一覧取得
  // -----------------------------
  const fetchPets = async () => {
    try {
      setLoading(true);

      const response = await fetch(`${API_BASE_URL}/api/pets`);

      if (!response.ok) {
        throw new Error('ペット情報を取得できませんでした');
      }

      const data = await response.json();

      setPets(data.pets);

      // 最初のペットを選択
      if (data.pets.length > 0) {
        setSelectedPet(data.pets[0]);
        setFormFromPet(data.pets[0]);
      } else {
        setSelectedPet(null);
        clearForm();
      }
    } catch (error) {
      console.error(error);
      Alert.alert('エラー', 'ペット情報の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };
  
  const savePet = async () => {
  try {
    if (!name.trim()) {
      Alert.alert('エラー', '名前を入力してください');
      return;
    }

    const isEditing = selectedPet !== null;

    const url = isEditing
      ? `${API_BASE_URL}/api/pets/${selectedPet.id}`
      : `${API_BASE_URL}/api/pets`;

    const response = await fetch(url, {
      method: isEditing ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: name.trim(),
        type: type.trim(),
        age: age ? Number(age) : null,
        weight: weight ? Number(weight) : null,
        note: note.trim(),
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error ||
        (isEditing
          ? 'ペット情報の更新に失敗しました'
          : 'ペットの登録に失敗しました')
      );
    }

    Alert.alert(
      '保存完了',
      isEditing
        ? 'ペット情報を更新しました'
        : 'ペットを登録しました'
    );

    await fetchPets();
    setViewMode('list');

  } catch (error) {
    console.error('保存エラー:', error);

    Alert.alert(
      'エラー',
      error instanceof Error
        ? error.message
        : 'ペットの保存に失敗しました'
    );
  }
};

  // -----------------------------
  // ペット情報をフォームへ反映
  // -----------------------------
  const setFormFromPet = (pet: Pet) => {
    setName(pet.name ?? '');
    setType(pet.type ?? '');
    setAge(pet.age !== null ? String(pet.age) : '');
    setWeight(pet.weight !== null ? String(pet.weight) : '');
    setNote(pet.note ?? '');
  };

  // -----------------------------
  // フォームを空にする
  // -----------------------------
  const clearForm = () => {
    setName('');
    setType('');
    setAge('');
    setWeight('');
    setNote('');
  };

  useEffect(() => {
    fetchPets();
  }, []);

  // -----------------------------
  // 読み込み中
  // -----------------------------
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>読み込み中...</Text>
      </View>
    );
  }

  return (
    <View style={styles.screen}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* ヘッダー */}
        <View style={styles.header}>
          <Text style={styles.title}>🐕 ペット</Text>

          {viewMode === 'profile' && pets.length > 0 && (
            <Pressable style={styles.petSwitcher}>
              <Text style={styles.petSwitcherText}>
                {selectedPet?.name ?? 'ペットを選択'}
              </Text>
              <Text style={styles.arrow}>▼</Text>
            </Pressable>
          )}
        </View>

        {/* プロフィール / ペット一覧 */}
        <View style={styles.viewTabs}>
          <Pressable
            style={[
              styles.viewTab,
              viewMode === 'profile' && styles.activeViewTab,
            ]}
            onPress={() => setViewMode('profile')}
          >
            <Text
              style={[
                styles.viewTabText,
                viewMode === 'profile' && styles.activeViewTabText,
              ]}
            >
              プロフィール
            </Text>
          </Pressable>

          <Pressable
            style={[
              styles.viewTab,
              viewMode === 'list' && styles.activeViewTab,
            ]}
            onPress={() => setViewMode('list')}
          >
            <Text
              style={[
                styles.viewTabText,
                viewMode === 'list' && styles.activeViewTabText,
              ]}
            >
              ペット一覧
            </Text>
          </Pressable>
        </View>

        {/* ========================= */}
        {/* プロフィール */}
        {/* ========================= */}
        {viewMode === 'profile' && (
          <>
            <View style={styles.profileCard}>
              {/* 写真 */}
              <View style={styles.photoArea}>
                <View style={styles.photoBox}>
                  {selectedPet?.photo ? (
                    <Image
                      source={{
                        uri: `${API_BASE_URL}/static/images/pets/${selectedPet.photo}`,
                      }}
                      style={styles.profilePhoto}
                    />
                  ) : (
                    <Text style={styles.photoPlaceholder}>🐕🐈</Text>
                  )}
                </View>

                <Pressable
                  style={styles.photoButton}
                  onPress={() =>
                    Alert.alert(
                      '写真',
                      '写真選択機能は次の段階で追加します'
                    )
                  }
                >
                  <Text style={styles.photoButtonText}>写真を選ぶ</Text>
                </Pressable>
              </View>

              {/* 基本情報 */}
              <View style={styles.infoArea}>
                {/* 名前 */}
                <View style={styles.inputGroup}>
                  <Text style={styles.label}>名前</Text>

                  <TextInput
                    value={name}
                    onChangeText={setName}
                    placeholder="例：ポチ"
                    maxLength={30}
                    style={styles.input}
                  />
                </View>

                {/* 種類 */}
                <View style={styles.inputGroup}>
                  <Text style={styles.label}>種類</Text>

                  <TextInput
                    value={type}
                    onChangeText={setType}
                    placeholder="例：柴犬"
                    maxLength={30}
                    style={styles.input}
                  />
                </View>

                {/* 年齢・体重 */}
                <View style={styles.inputRow}>
                  <View style={styles.halfInput}>
                    <Text style={styles.label}>年齢</Text>

                    <View style={styles.unitInput}>
                      <TextInput
                        value={age}
                        onChangeText={setAge}
                        placeholder="3"
                        keyboardType="numeric"
                        style={styles.numberInput}
                      />
                      <Text style={styles.unit}>歳</Text>
                    </View>
                  </View>

                  <View style={styles.halfInput}>
                    <Text style={styles.label}>体重</Text>

                    <View style={styles.unitInput}>
                      <TextInput
                        value={weight}
                        onChangeText={setWeight}
                        placeholder="8.5"
                        keyboardType="decimal-pad"
                        style={styles.numberInput}
                      />
                      <Text style={styles.unit}>kg</Text>
                    </View>
                  </View>
                </View>

                {/* その他 */}
                <View style={styles.inputGroup}>
                  <Text style={styles.label}>その他の基本情報</Text>

                  <TextInput
                    value={note}
                    onChangeText={setNote}
                    placeholder="性格・アレルギー・注意事項など"
                    multiline
                    maxLength={500}
                    style={styles.textArea}
                  />
                </View>

                {/* 保存 */}
                <Pressable
                  style={styles.saveButton}
                  onPress={savePet}
                >
                  <Text style={styles.saveButtonText}>保存する</Text>
                </Pressable>
              </View>
            </View>

            {/* 削除 */}
            {selectedPet && (
              <Pressable
                style={styles.deleteButton}
                onPress={() =>
                  Alert.alert(
                    'ペットを削除',
                    `「${selectedPet.name}」を削除しますか？`,
                    [
                      {
                        text: 'キャンセル',
                        style: 'cancel',
                      },
                      {
                        text: '削除',
                        style: 'destructive',
                        onPress: () => {
                          Alert.alert(
                            '確認',
                            '削除APIは次の段階で接続します'
                          );
                        },
                      },
                    ]
                  )
                }
              >
                <Text style={styles.deleteButtonText}>
                  ペットを削除
                </Text>
              </Pressable>
            )}
          </>
        )}

        {/* ========================= */}
        {/* ペット一覧 */}
        {/* ========================= */}
        {viewMode === 'list' && (
          <>
            {pets.length > 0 ? (
              <View style={styles.petList}>
                {pets.map((pet) => (
                  <View key={pet.id} style={styles.petListCard}>
                    {/* 写真 */}
                    <View style={styles.listPhoto}>
                      {pet.photo ? (
                        <Image
                          source={{
                            uri: `${API_BASE_URL}/static/images/pets/${pet.photo}`,
                          }}
                          style={styles.listPhotoImage}
                        />
                      ) : (
                        <Text style={styles.listPhotoPlaceholder}>
                          🐾
                        </Text>
                      )}
                    </View>

                    {/* 情報 */}
                    <View style={styles.listInfo}>
                      <Text style={styles.petName}>
                        {pet.name}
                      </Text>

                      {pet.type ? (
                        <Text style={styles.petType}>
                          {pet.type}
                        </Text>
                      ) : null}

                      <Text style={styles.basicInfo}>
                        {pet.age !== null
                          ? `${pet.age}歳`
                          : '年齢未登録'}
                        {' / '}
                        {pet.weight !== null
                          ? `${pet.weight}kg`
                          : '体重未登録'}
                      </Text>

                      <Pressable
                        onPress={() => {
                          setSelectedPet(pet);
                          setFormFromPet(pet);
                          setViewMode('profile');
                        }}
                      >
                        <Text style={styles.detailLink}>
                          詳細を見る
                        </Text>
                      </Pressable>
                    </View>
                  </View>
                ))}
              </View>
            ) : (
              <Text style={styles.emptyText}>
                まだペットが登録されていません。
              </Text>
            )}

            {/* ペット追加 */}
            <Pressable
              style={styles.addButton}
              onPress={() => {
                setSelectedPet(null);
                clearForm();
                setViewMode('profile');
              }}
            >
              <Text style={styles.addButtonText}>
                ＋ ペットを追加
              </Text>
            </Pressable>
          </>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#000',
  },

  content: {
    padding: 24,
    paddingBottom: 120,
  },

  loadingContainer: {
    flex: 1,
    backgroundColor: '#000',
    alignItems: 'center',
    justifyContent: 'center',
  },

  loadingText: {
    color: '#fff',
    marginTop: 12,
  },

  header: {
    marginBottom: 20,
  },

  title: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 16,
  },

  petSwitcher: {
    backgroundColor: '#181818',
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 18,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },

  petSwitcherText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },

  arrow: {
    color: '#aaa',
    fontSize: 12,
  },

  viewTabs: {
    flexDirection: 'row',
    backgroundColor: '#181818',
    borderRadius: 12,
    padding: 4,
    marginBottom: 20,
  },

  viewTab: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 9,
  },

  activeViewTab: {
    backgroundColor: '#fff',
  },

  viewTabText: {
    color: '#aaa',
    fontWeight: '600',
  },

  activeViewTabText: {
    color: '#000',
  },

  profileCard: {
    backgroundColor: '#111',
    borderRadius: 18,
    padding: 20,
  },

  photoArea: {
    alignItems: 'center',
    marginBottom: 24,
  },

  photoBox: {
    width: 180,
    height: 180,
    borderRadius: 20,
    backgroundColor: '#1d1d1d',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },

  profilePhoto: {
    width: '100%',
    height: '100%',
  },

  photoPlaceholder: {
    fontSize: 50,
  },

  photoButton: {
    marginTop: 12,
    backgroundColor: '#292929',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 20,
  },

  photoButtonText: {
    color: '#fff',
    fontWeight: '600',
  },

  infoArea: {
    gap: 16,
  },

  inputGroup: {
    gap: 7,
  },

  label: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },

  input: {
    backgroundColor: '#1d1d1d',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 13,
    color: '#fff',
    fontSize: 16,
  },

  inputRow: {
    flexDirection: 'row',
    gap: 12,
  },

  halfInput: {
    flex: 1,
    gap: 7,
  },

  unitInput: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1d1d1d',
    borderRadius: 10,
    paddingRight: 12,
  },

  numberInput: {
    flex: 1,
    paddingHorizontal: 14,
    paddingVertical: 13,
    color: '#fff',
    fontSize: 16,
  },

  unit: {
    color: '#aaa',
  },

  textArea: {
    minHeight: 120,
    backgroundColor: '#1d1d1d',
    borderRadius: 10,
    padding: 14,
    color: '#fff',
    fontSize: 16,
    textAlignVertical: 'top',
  },

  saveButton: {
    backgroundColor: '#fff',
    borderRadius: 12,
    alignItems: 'center',
    paddingVertical: 15,
    marginTop: 4,
  },

  saveButtonText: {
    color: '#000',
    fontSize: 16,
    fontWeight: 'bold',
  },

  deleteButton: {
    marginTop: 16,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 12,
    alignItems: 'center',
    paddingVertical: 14,
  },

  deleteButtonText: {
    color: '#fff',
    fontWeight: '600',
  },

  petList: {
    gap: 14,
  },

  petListCard: {
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 14,
    flexDirection: 'row',
    gap: 16,
  },

  listPhoto: {
    width: 90,
    height: 90,
    borderRadius: 14,
    backgroundColor: '#1d1d1d',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },

  listPhotoImage: {
    width: '100%',
    height: '100%',
  },

  listPhotoPlaceholder: {
    fontSize: 32,
  },

  listInfo: {
    flex: 1,
    justifyContent: 'center',
  },

  petName: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },

  petType: {
    color: '#aaa',
    marginTop: 4,
  },

  basicInfo: {
    color: '#ccc',
    marginTop: 8,
  },

  detailLink: {
    color: '#fff',
    fontWeight: '600',
    marginTop: 10,
    textDecorationLine: 'underline',
  },

  emptyText: {
    color: '#aaa',
    textAlign: 'center',
    marginTop: 40,
  },

  addButton: {
    marginTop: 20,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
  },

  addButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
});