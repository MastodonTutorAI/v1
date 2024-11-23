
upload_button = """
    <style>
    .element-container:has(style){
        display: none;
    }
    #upload_button {
        display: none;
    }
    .element-container:has(#upload_button) {
        display: none;
    }
    .element-container:has(#upload_button) + div {
        padding-top: 50px;
    }
    </style>
    """