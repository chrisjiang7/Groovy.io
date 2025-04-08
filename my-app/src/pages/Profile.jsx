import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { mdiAccountConvert } from "@mdi/js";
import Icon from "@mdi/react";
import { auth, db } from "../firebase";
import { doc, getDoc, updateDoc } from "firebase/firestore";
import { updateEmail, updatePassword, EmailAuthProvider, reauthenticateWithCredential } from "firebase/auth";

const Profile = () => {
  const navigate = useNavigate();
  const [editMode, setEditMode] = useState(false);
  const [profile, setProfile] = useState(null);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Fetch user profile from Firestore
  useEffect(() => {
    const fetchProfile = async () => {
      const user = auth.currentUser;
      if (!user) return;

      try {
        const docRef = doc(db, "users", user.uid);
        const docSnap = await getDoc(docRef);
        if (docSnap.exists()) {
          const data = docSnap.data();
          setProfile({
            username: data.username || "",
            email: data.email || user.email || "",
            password: "••••••••",
            accountCreated: new Date(data.createdAt).toDateString(),
            favoritePlaylist: data.favoritePlaylist || "None",
            totalRemixes: data.totalRemixes || 0,
          });
        } else {
          alert("No profile found for this user.");
        }
      } catch (error) {
        console.error("Error loading profile:", error);
        alert("Error loading profile.");
      }
    };

    fetchProfile();
  }, []);

  const handleChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    try {
      const user = auth.currentUser;
      if (!user) return;

      // Reauthenticate if changing email or password
      if (profile.email !== user.email || newPassword) {
        const credential = EmailAuthProvider.credential(
          user.email,
          currentPassword
        );
        await reauthenticateWithCredential(user, credential);
      }

      // Update password if new password provided
      if (newPassword) {
        if (newPassword !== confirmPassword) {
          throw new Error("New passwords don't match");
        }
        await updatePassword(user, newPassword);
      }

      // Update email if changed
      if (profile.email !== user.email) {
        await updateEmail(user, profile.email);
      }

      // Update Firestore
      await updateDoc(doc(db, "users", user.uid), {
        username: profile.username,
        email: profile.email,
      });

      alert("Profile updated successfully!");
      setEditMode(false);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      console.error("Error updating profile:", error);
      alert("Failed to update profile: " + error.message);
    }
  };

  const handleLogout = async () => {
    await auth.signOut();
    navigate("/");
  };

  if (!profile) {
    return (
      <div className="text-white text-center mt-20 text-xl">
        Loading your profile...
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center p-8 pb-24 w-full">
      <h1 className="text-4xl font-bold mb-10 text-purple-400">Your Profile</h1>

      <div className="relative bg-gray-800 p-8 rounded-2xl shadow-lg w-full max-w-4xl flex flex-col lg:flex-row items-center gap-8">
        {/* Profile Picture */}
        <div className="w-50 h-50 rounded-full bg-cyan-600 flex items-center justify-center text-white text-3xl font-semibold">
          <Icon path={mdiAccountConvert} size={6} color="#afeafa" />
        </div>

        {/* User Info Section */}
        <div className="flex flex-col w-full gap-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Username */}
            <div className="flex flex-col">
              <label className="block text-sm font-bold text-purple-400 mb-2">Username</label>
              <div className="pb-2 border-b border-gray-700">
                {editMode ? (
                  <input
                    type="text"
                    name="username"
                    value={profile.username}
                    onChange={handleChange}
                    className="w-full p-2 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                ) : (
                  <p className="text-lg">{profile.username}</p>
                )}
              </div>
            </div>

            {/* Email */}
            <div className="flex flex-col">
              <label className="block text-sm font-bold text-purple-400 mb-2">Email</label>
              <div className="pb-2 border-b border-gray-700">
                {editMode ? (
                  <input
                    type="email"
                    name="email"
                    value={profile.email}
                    onChange={handleChange}
                    className="w-full p-2 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                ) : (
                  <p className="text-lg">{profile.email}</p>
                )}
              </div>
            </div>

            {/* Password */}
            <div className="flex flex-col">
              <label className="block text-sm font-bold text-purple-400 mb-2">Password</label>
              <div className="pb-2 border-b border-gray-700">
                {editMode ? (
                  <div className="space-y-4">
                    <input
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className="w-full p-2 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="Current password (required for changes)"
                      required
                    />
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full p-2 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                      placeholder="New password (leave blank to keep current)"
                    />
                    {newPassword && (
                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full p-2 rounded bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Confirm new password"
                      />
                    )}
                  </div>
                ) : (
                  <p className="text-lg">••••••••</p>
                )}
              </div>
            </div>

            {/* Account Created On */}
            <div className="flex flex-col">
              <label className="block text-sm font-bold text-purple-400 mb-2">Account Created On</label>
              <div className="pb-2 border-b border-gray-700">
                <p className="text-lg">{profile.accountCreated}</p>
              </div>
            </div>

            {/* Favorite Playlist */}
            <div className="flex flex-col">
              <label className="block text-sm font-bold text-purple-400 mb-2">Favorite Playlist</label>
              <div className="pb-2 border-b border-gray-700">
                <p className="text-lg">{profile.favoritePlaylist}</p>
              </div>
            </div>

            {/* Total Remixes */}
            <div className="flex flex-col">
              <label className="block text-sm font-bold text-purple-400 mb-2">Total Remixes Created</label>
              <div className="pb-2 border-b border-gray-700">
                <p className="text-lg">{profile.totalRemixes}</p>
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex justify-between items-center mt-2">
            {editMode ? (
              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  className="bg-green-500 text-white p-2 px-4 rounded-lg hover:bg-green-600 transition-transform transform hover:scale-105"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setEditMode(false);
                    setCurrentPassword("");
                    setNewPassword("");
                    setConfirmPassword("");
                  }}
                  className="bg-gray-600 text-white p-2 px-4 rounded-lg hover:bg-gray-500 transition-transform transform hover:scale-105"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => setEditMode(true)}
                className="bg-cyan-600 text-white p-2 px-4 rounded-lg hover:bg-cyan-700 transition-transform transform hover:scale-105"
              >
                Edit Profile
              </button>
            )}

            <button
              onClick={handleLogout}
              className="bg-red-500 text-white p-2 px-4 rounded-lg hover:bg-red-600 transition-transform transform hover:scale-105"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;