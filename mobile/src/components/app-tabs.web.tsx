import { Tabs } from 'expo-router';

export default function AppTabs() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{ title: 'ホーム' }}
      />

      <Tabs.Screen
        name="pets"
        options={{ title: 'ペット' }}
      />

      <Tabs.Screen
        name="calendar"
        options={{ title: 'カレンダー' }}
      />

      <Tabs.Screen
        name="records"
        options={{ title: '記録' }}
      />

      <Tabs.Screen
        name="reservation"
        options={{ title: '予約' }}
      />
    </Tabs>
  );
}