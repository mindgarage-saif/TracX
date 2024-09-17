colorPrimary = "#388E3C"
colorPrimaryDark = "#1B5E20"
colorOnPrimary = "#ffffff"

colorSecondary = "#1976D2"
colorSecondaryDark = "#263238"
colorOnSecondary = "#ffffff"

colorError = "#D32F2F"
colorErrorDark = "#B71C1C"
colorOnError = "#ffffff"

colorNeutral = "#455A64"
colorNeutralDark = "#40484c"
colorOnNeutral = "#ffffff"

startButtonStyle = f"""
    QPushButton {{
        background-color: {colorPrimary};
        color: {colorOnPrimary};
    }}
                                
    QPushButton:hover {{
        background-color: {colorPrimaryDark};
        color: {colorOnPrimary};
    }}

    QPushButton:disabled {{
        background-color: {colorNeutral};
        color: {colorOnNeutral};
    }}
"""

pauseButtonStyle = f"""
    QPushButton {{
        background-color: {colorSecondary};
        color: {colorOnSecondary};
    }}
                                
    QPushButton:hover {{
        background-color: {colorSecondaryDark};
        color: {colorOnSecondary};
    }}

    QPushButton:disabled {{
        background-color: {colorNeutral};
        color: {colorOnNeutral};
    }}
"""

stopButtonStyle = f"""
    QPushButton {{
        background-color: {colorError};
        color: {colorOnError};
    }}
                                
    QPushButton:hover {{
        background-color: {colorErrorDark};
        color: {colorOnError};
    }}

    QPushButton:disabled {{
        background-color: {colorNeutral};
        color: {colorOnNeutral};
    }}
"""
